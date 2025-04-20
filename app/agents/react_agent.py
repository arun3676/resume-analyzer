"""
Implementation of the ReAct agent for resume analysis using Gemini API with rate limiting.
"""
from typing import Dict, List, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import time
import os
import hashlib
import json
import pickle
from pathlib import Path

from app.config import GEMINI_API_KEY, DEFAULT_MODEL, TEMPERATURE
from app.agents.prompts import REACT_SYSTEM_PROMPT, RESUME_ANALYSIS_PROMPT
from app.agents.tools import get_resume_tools

# Rate limiting settings
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 10  # Seconds between requests

# Cache directory
CACHE_DIR = Path("resume_cache")
CACHE_DIR.mkdir(exist_ok=True)

class ResumeReactAgent:
    """
    ReAct agent implementation for resume analysis.
    """
    
    def __init__(self):
        """Initialize the ReAct agent with necessary components."""
        # Initialize the language model with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            temperature=TEMPERATURE,
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            convert_system_message_to_human=True  # Gemini doesn't support system messages natively
        )
        
        # Get available tools
        self.tools = get_resume_tools()
        
        # Create the agent (don't initialize yet to avoid API calls)
        self.agent_executor = None
    
    def _create_agent(self):
        """Create a functional agent using initialize_agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10  # Reduced from 15 to use fewer API calls
        )
    
    def _get_agent_executor(self):
        """Get or create the agent executor with lazy initialization."""
        if self.agent_executor is None:
            self.agent_executor = self._create_agent()
        return self.agent_executor
    
    def _shorten_text(self, text, max_length=3000):
        """Shorten text to avoid context length issues."""
        if len(text) <= max_length:
            return text
        # Keep first and last parts of the text
        first_part = text[:max_length//2]
        last_part = text[-max_length//2:]
        return first_part + "\n...[content truncated for brevity]...\n" + last_part
    
    def _get_cache_key(self, resume_text, job_description):
        """Generate a cache key for the analysis request."""
        content = f"{resume_text}|{job_description}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, cache_key):
        """Check if analysis is already in cache."""
        cache_file = CACHE_DIR / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except:
                return None
        return None
    
    def _save_to_cache(self, cache_key, result):
        """Save analysis result to cache."""
        cache_file = CACHE_DIR / f"{cache_key}.pkl"
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
    
    def direct_analyze(self, resume_text, job_description=None):
        """
        Analyze resume directly with the LLM without using the agent.
        Used as fallback when rate limits are hit.
        """
        prompt = f"""
        Analyze this resume and provide a detailed assessment:
        
        RESUME:
        {resume_text}
        """
        
        if job_description:
            prompt += f"""
            
            JOB DESCRIPTION:
            {job_description}
            
            Please provide:
            1. Key skills and experience identified in the resume
            2. Strengths and weaknesses of the candidate
            3. Match percentage with the job description (scale of 0-100%)
            4. Suggestions for improvement
            """
        else:
            prompt += """
            
            Please provide:
            1. Key skills and experience identified in the resume
            2. Strengths and weaknesses of the candidate
            3. Suggestions for improvement
            """
            
        response = self.llm.invoke(prompt)
        
        return {
            "analysis": response.content,
            "thought_process": [],
            "success": True
        }
    
    def analyze_resume(self, 
                      resume_text: str, 
                      job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a resume and optionally compare it to a job description.
        """
        global LAST_REQUEST_TIME
        
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - LAST_REQUEST_TIME
        
        if time_since_last_request < MIN_REQUEST_INTERVAL:
            # If we hit rate limits, wait and then use direct analysis
            wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
            time.sleep(wait_time)  # Wait to respect rate limits
        
        LAST_REQUEST_TIME = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(resume_text, job_description)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Shorten the texts to avoid context length issues
        resume_text = self._shorten_text(resume_text)
        if job_description:
            job_description = self._shorten_text(job_description, max_length=1500)
        
        # Add job description context if provided
        job_desc_text = f"Job Description: {job_description}" if job_description else ""
        
        # Create the full input prompt
        input_text = RESUME_ANALYSIS_PROMPT.format(
            resume_text=resume_text,
            job_description=job_desc_text
        )
        
        try:
            # Try using the agent first
            try:
                agent_executor = self._get_agent_executor()
                result = agent_executor.invoke({"input": input_text})
                
                response = {
                    "analysis": result["output"],
                    "thought_process": result.get("intermediate_steps", []),
                    "success": True
                }
                
            except Exception as e:
                # If agent fails, fall back to direct analysis
                print(f"Agent failed with error: {str(e)}. Falling back to direct analysis.")
                response = self.direct_analyze(resume_text, job_description)
            
            # Cache the result
            self._save_to_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            return {
                "analysis": f"Error analyzing resume: {str(e)}",
                "thought_process": [],
                "success": False
            }