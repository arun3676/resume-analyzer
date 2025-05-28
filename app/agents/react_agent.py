"""
Implementation of the ReAct agent for resume analysis using Gemini API with rate limiting.
"""
from typing import Dict, List, Any, Optional
# from langchain_google_genai import ChatGoogleGenerativeAI # Commented out Gemini
from langchain_openai import ChatOpenAI # Added OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import time
import os
import hashlib
import json
import pickle
from pathlib import Path

from app.config import OPENAI_API_KEY, DEEPSEEK_API_KEY, LLM_PROVIDER, DEFAULT_MODEL, TEMPERATURE # Added DEEPSEEK_API_KEY and LLM_PROVIDER
from app.agents.prompts import REACT_SYSTEM_PROMPT, RESUME_ANALYSIS_PROMPT
from app.agents.tools import get_resume_tools, match_skills_tool
from app.models.schema import InterviewQuestion, InterviewQuestionsResponse, MockInterviewFeedbackResponse, SalaryIntelligenceResponse, SalaryRange, MarketPositioning, NegotiationStrategy # Added new models

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
        if LLM_PROVIDER == "deepseek":
            self.llm = ChatOpenAI(
                model_name=DEFAULT_MODEL,
                temperature=TEMPERATURE,
                openai_api_key=DEEPSEEK_API_KEY,
                openai_api_base="https://api.deepseek.com"
            )
        elif LLM_PROVIDER == "openai":
            self.llm = ChatOpenAI(
                model_name=DEFAULT_MODEL,
                temperature=TEMPERATURE,
                openai_api_key=OPENAI_API_KEY
            )
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. Supported providers are 'openai' and 'deepseek'.")
        
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
            max_iterations=20,  # Increased from 10 to 20
            max_execution_time=300,  # Added 5 minute timeout
            # Ensure system prompt is handled correctly if agent type expects it
            # For some OpenAI models/agents, you might need to pass it differently or ensure it's part of messages
            agent_kwargs={
                "system_message": REACT_SYSTEM_PROMPT
            }
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
        You are an expert resume analyst. Analyze this resume thoroughly and provide detailed insights.
        
        RESUME:
        {resume_text}
        """
        
        skill_match_details = None
        if job_description:
            prompt += f"""
            
            JOB DESCRIPTION:
            {job_description}
            
            Please provide a comprehensive analysis with specific focus on job matching:
            
            1. **OVERALL MATCH ASSESSMENT**: 
               - Provide a clear YES/NO recommendation on whether this candidate should apply for this role
               - Explain the reasoning behind your recommendation
               - Give a match confidence score (0-100%)
            
            2. **SKILLS ANALYSIS**: 
               - List all technical skills found in the resume
               - Identify which skills match the job requirements
               - Highlight missing critical skills for this role
            
            3. **EXPERIENCE EVALUATION**: 
               - Assess how the candidate's experience aligns with job requirements
               - Identify relevant projects or achievements that stand out
               - Note any experience gaps
            
            4. **EDUCATION & CERTIFICATIONS**: 
               - Review educational background relevance to the role
               - Suggest additional certifications that would strengthen the application
            
            5. **KEY STRENGTHS FOR THIS ROLE**: 
               - Highlight the candidate's strongest points for this specific position
               - Mention unique selling points that make them stand out
            
            6. **CRITICAL AREAS FOR IMPROVEMENT**: 
               - List 3-5 specific skills the candidate should develop before applying
               - Prioritize these improvements by importance for the role
               - Suggest learning resources or ways to gain these skills
            
            7. **APPLICATION STRATEGY**: 
               - Recommend when to apply (now vs. after skill development)
               - Suggest how to position their application effectively
               - Provide tips for highlighting relevant experience
            
            8. **OVERALL RECOMMENDATION**: 
               - Clear final verdict: "STRONGLY RECOMMEND APPLYING" / "APPLY WITH PREPARATION" / "IMPROVE SKILLS FIRST"
               - Expected success probability if they apply now
               - Timeline for skill improvement if needed
            
            Format your response clearly with headers and bullet points. Be honest and constructive in your assessment.
            """
            # Perform skill matching
            try:
                skill_match_details = match_skills_tool(resume_text, job_description)
            except Exception as e:
                print(f"Skill matching failed: {e}")
                skill_match_details = {
                    "matched_skills": [],
                    "resume_skills": [],
                    "job_description_skills": [],
                    "match_percentage": 0.0
                }
        else:
            prompt += """
            
            Please provide a comprehensive analysis including:
            
            1. **SKILLS ANALYSIS**: Identify all technical and soft skills mentioned in the resume
            2. **EXPERIENCE EVALUATION**: Assess the candidate's work experience and career progression
            3. **EDUCATION ASSESSMENT**: Review educational background
            4. **STRENGTHS**: List the candidate's key strengths
            5. **AREAS FOR IMPROVEMENT**: Suggest specific improvements
            6. **RECOMMENDATIONS**: Provide actionable advice for the candidate
            
            Format your response clearly with headers and bullet points for easy reading.
            """
            
        # For ChatOpenAI, the input should be a list of messages
        messages = [
            SystemMessage(content="You are an expert resume analyst with years of experience in HR and recruitment. Provide detailed, actionable insights."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            analysis_content = response.content
        except Exception as e:
            analysis_content = f"Error during analysis: {str(e)}. However, I can still provide skill matching details if a job description was provided."
        
        result = {
            "analysis": analysis_content,
            "thought_process": [],
            "success": True
        }
        if skill_match_details:
            result["skill_match_details"] = skill_match_details
        
        return result
    
    def analyze_resume(self, 
                      resume_text: str, 
                      job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a resume and optionally compare it to a job description.
        """
        print("DEBUG: analyze_resume called with direct analysis approach")  # Debug print
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
        # cached_result = self._check_cache(cache_key)  # Temporarily disabled for testing
        # if cached_result:
        #     return cached_result
        
        # Shorten the texts to avoid context length issues
        resume_text = self._shorten_text(resume_text)
        if job_description:
            job_description = self._shorten_text(job_description, max_length=1500)

        try:
            # Use direct analysis for more reliable results
            # The agent often hits iteration limits, so direct analysis is more stable
            response = self.direct_analyze(resume_text, job_description)
            
            # Cache the result
            self._save_to_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            final_response = {
                "analysis": f"Error analyzing resume: {str(e)}",
                "thought_process": [],
                "success": False
            }
            return final_response

    def generate_interview_questions(self, resume_text: str, job_description: str, question_types: List[str], num_questions: int) -> InterviewQuestionsResponse:
        """
        Generate personalized interview questions using the LLM.
        """
        global LAST_REQUEST_TIME
        current_time = time.time()
        time_since_last_request = current_time - LAST_REQUEST_TIME
        if time_since_last_request < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
            time.sleep(wait_time)
        LAST_REQUEST_TIME = time.time()

        resume_text_short = self._shorten_text(resume_text)
        job_description_short = self._shorten_text(job_description)
        question_types_str = ", ".join(question_types)

        # Create prompt directly using string formatting
        system_prompt = """You are an expert interview coach and hiring manager.
Your task is to generate relevant interview questions based on the provided resume and job description.
Ensure the questions cover the specified types and are tailored to the candidate's experience and the role's requirements.
For behavioral questions, explicitly mention that the candidate should use the STAR method for their answer.
Output should be a JSON list of questions, where each question is an object with 'question', 'type', and optionally 'expected_answer_format' fields.
Example:
[
    {"question": "Can you describe your experience with deploying applications on AWS?", "type": "technical"},
    {"question": "Tell me about a time you had to overcome a significant challenge in a project. (Use STAR method)", "type": "behavioral", "expected_answer_format": "STAR method"}
]"""

        human_prompt = f"""Please generate {num_questions} interview questions.
Question types to include: {question_types_str}

RESUME:
{resume_text_short}

JOB DESCRIPTION:
{job_description_short}

Generate the questions now."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        try:
            response = self.llm.invoke(messages)
            response_content = response.content
            # The LLM is expected to return a JSON string representation of a list of questions
            generated_questions_data = json.loads(response_content)
            
            questions = [InterviewQuestion(**q_data) for q_data in generated_questions_data]
            # Ensure we don't exceed num_questions, in case the LLM generates more
            questions = questions[:num_questions]

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM for interview questions: {e}")
            print(f"LLM Response content: {response.content if 'response' in locals() else 'No response'}")
            # Fallback or error handling
            questions = [InterviewQuestion(question="Error: Could not generate questions due to LLM response format.", type="error")]
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            questions = [InterviewQuestion(question=f"Error: Could not generate questions. {str(e)}", type="error")]
            
        return InterviewQuestionsResponse(questions=questions)

    def get_mock_interview_feedback(self, question: str, user_answer: str, job_description: Optional[str]) -> MockInterviewFeedbackResponse:
        """
        Provide AI-driven feedback on a user's answer to an interview question using the LLM.
        """
        global LAST_REQUEST_TIME
        current_time = time.time()
        time_since_last_request = current_time - LAST_REQUEST_TIME
        if time_since_last_request < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
            time.sleep(wait_time)
        LAST_REQUEST_TIME = time.time()

        job_description_short = self._shorten_text(job_description) if job_description else "N/A"
        user_answer_short = self._shorten_text(user_answer, max_length=1000)

        # Create prompt directly using string formatting
        system_prompt = """You are an expert interview feedback provider.
Analyze the user's answer to the interview question and provide constructive feedback.
Consider the clarity, conciseness, relevance to the question, and use of examples (like STAR method if applicable).
Provide an overall feedback message, an optional score (0.0 to 1.0), and specific suggestions for improvement.
Output should be a JSON object with 'feedback', 'score', and 'suggestions_for_improvement' fields.
Example:
{
    "feedback": "Your answer was quite detailed, but you could have focused more on the specific outcome of your actions. Good use of an example project.",
    "score": 0.7,
    "suggestions_for_improvement": ["Try to quantify the impact of your actions more explicitly.", "Ensure your STAR method explanation clearly links the Situation to the Result."]
}"""

        human_prompt = f"""Please provide feedback on my answer to the following interview question.
Job Description (for context, if available):
{job_description_short}

Question:
{question}

My Answer:
{user_answer_short}

Provide your feedback now."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        try:
            response = self.llm.invoke(messages)
            response_content = response.content
            # The LLM is expected to return a JSON string representation of the feedback object
            feedback_data = json.loads(response_content)
            
            # Validate and construct the response object
            feedback_text = feedback_data.get("feedback", "Error: Could not parse feedback text.")
            score = feedback_data.get("score")
            suggestions = feedback_data.get("suggestions_for_improvement")
            
            # Ensure suggestions is a list of strings if present
            if suggestions is not None and not all(isinstance(s, str) for s in suggestions):
                suggestions = ["Error: LLM returned suggestions in an unexpected format."]

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM for interview feedback: {e}")
            print(f"LLM Response content: {response.content if 'response' in locals() else 'No response'}")
            feedback_text = "Error: Could not get feedback due to LLM response format."
            score = None
            suggestions = None
        except Exception as e:
            print(f"Error getting mock interview feedback: {e}")
            feedback_text = f"Error: Could not get feedback. {str(e)}"
            score = None
            suggestions = None

        return MockInterviewFeedbackResponse(
            feedback=feedback_text,
            score=score,
            suggestions_for_improvement=suggestions
        )

    def analyze_salary_intelligence(self, resume_text: str, job_title: str, location: str, 
                                  years_of_experience: Optional[int] = None, 
                                  company_size: Optional[str] = None, 
                                  industry: Optional[str] = None) -> SalaryIntelligenceResponse:
        """
        Analyze salary intelligence using AI to predict salary ranges and provide market insights.
        """
        global LAST_REQUEST_TIME
        current_time = time.time()
        time_since_last_request = current_time - LAST_REQUEST_TIME
        if time_since_last_request < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
            time.sleep(wait_time)
        LAST_REQUEST_TIME = time.time()

        resume_text_short = self._shorten_text(resume_text)
        
        # Create comprehensive prompt for salary analysis
        system_prompt = """You are an expert salary analyst and career advisor with access to comprehensive market data.
Your task is to analyze the provided resume and job details to predict salary ranges, market positioning, and negotiation strategies.
You must provide realistic, data-driven insights based on current market conditions.

Output should be a JSON object with the following structure:
{
    "predicted_salary_range": {
        "min_salary": 75000,
        "max_salary": 95000,
        "median_salary": 85000,
        "currency": "USD"
    },
    "market_positioning": {
        "percentile": 75.5,
        "positioning_text": "You're in the top 25% for your role and experience level",
        "comparison_factors": ["Strong technical skills", "Relevant experience", "In-demand location"]
    },
    "negotiation_strategies": [
        {
            "strategy_type": "moderate",
            "key_points": ["Highlight unique skills", "Reference market data"],
            "timing_advice": "Best to negotiate after receiving initial offer",
            "leverage_factors": ["High-demand skills", "Multiple offers"]
        }
    ],
    "skill_value_analysis": {
        "Python": 8.5,
        "Machine Learning": 9.2,
        "AWS": 7.8
    },
    "location_adjustment": 15.5,
    "experience_premium": 12.0,
    "recommendations": ["Consider pursuing cloud certifications", "Highlight leadership experience"],
    "data_confidence": 0.85
}"""

        human_prompt = f"""Please analyze the salary intelligence for this candidate:

JOB TITLE: {job_title}
LOCATION: {location}
YEARS OF EXPERIENCE: {years_of_experience or 'Not specified'}
COMPANY SIZE: {company_size or 'Not specified'}
INDUSTRY: {industry or 'Not specified'}

RESUME:
{resume_text_short}

Provide a comprehensive salary analysis including:
1. Realistic salary range prediction based on skills, experience, and location
2. Market positioning analysis (what percentile they're in)
3. Multiple negotiation strategies (conservative, moderate, aggressive)
4. Skill-by-skill value analysis (rate each skill 1-10 for market value)
5. Location and experience adjustments
6. Actionable recommendations for salary improvement
7. Confidence level in the analysis

Consider current market trends, skill demand, and geographic factors."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        try:
            response = self.llm.invoke(messages)
            response_content = response.content
            
            # Parse the JSON response
            salary_data = json.loads(response_content)
            
            # Construct the response object
            predicted_range = SalaryRange(**salary_data["predicted_salary_range"])
            market_pos = MarketPositioning(**salary_data["market_positioning"])
            
            negotiation_strategies = [
                NegotiationStrategy(**strategy) 
                for strategy in salary_data["negotiation_strategies"]
            ]
            
            return SalaryIntelligenceResponse(
                predicted_salary_range=predicted_range,
                market_positioning=market_pos,
                negotiation_strategies=negotiation_strategies,
                skill_value_analysis=salary_data["skill_value_analysis"],
                location_adjustment=salary_data["location_adjustment"],
                experience_premium=salary_data["experience_premium"],
                recommendations=salary_data["recommendations"],
                data_confidence=salary_data["data_confidence"]
            )

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM for salary intelligence: {e}")
            print(f"LLM Response content: {response.content if 'response' in locals() else 'No response'}")
            
            # Return fallback response
            return SalaryIntelligenceResponse(
                predicted_salary_range=SalaryRange(
                    min_salary=50000, max_salary=80000, median_salary=65000
                ),
                market_positioning=MarketPositioning(
                    percentile=50.0,
                    positioning_text="Unable to determine exact positioning due to analysis error",
                    comparison_factors=["Analysis error occurred"]
                ),
                negotiation_strategies=[
                    NegotiationStrategy(
                        strategy_type="moderate",
                        key_points=["Research market rates", "Highlight your value"],
                        timing_advice="Negotiate after receiving offer",
                        leverage_factors=["Your unique skills and experience"]
                    )
                ],
                skill_value_analysis={},
                location_adjustment=0.0,
                experience_premium=0.0,
                recommendations=["Error occurred during analysis. Please try again."],
                data_confidence=0.0
            )
            
        except Exception as e:
            print(f"Error analyzing salary intelligence: {e}")
            
            # Return error response
            return SalaryIntelligenceResponse(
                predicted_salary_range=SalaryRange(
                    min_salary=0, max_salary=0, median_salary=0
                ),
                market_positioning=MarketPositioning(
                    percentile=0.0,
                    positioning_text=f"Error: {str(e)}",
                    comparison_factors=["Analysis failed"]
                ),
                negotiation_strategies=[],
                skill_value_analysis={},
                location_adjustment=0.0,
                experience_premium=0.0,
                recommendations=[f"Error occurred: {str(e)}"],
                data_confidence=0.0
            )