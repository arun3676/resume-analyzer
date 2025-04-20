"""
FastAPI application for Resume Analyzer.
"""
import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import mlflow
from io import BytesIO
import time
import os
from dotenv import load_dotenv

load_dotenv()

from app.config import APP_NAME, APP_VERSION, DEBUG, MLFLOW_TRACKING_URI, EXPERIMENT_NAME
from app.models.schema import ResumeAnalysisRequest, ResumeAnalysisResponse
from app.agents.react_agent import ResumeReactAgent
from app.services.parser import extract_skills, extract_experience, extract_education
from app.services.analyzer import analyze_strengths_weaknesses, calculate_job_match, suggest_improvements
from app.services.vector_store import initialize_vector_store
from app.services.logging import initialize_promptlayer
from app.services.structured_analyzer import StructuredAnalyzer

# Initialize the FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="An AI-powered resume analyzer using ReAct agents",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=DEBUG
)

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

# Initialize analyzers
agent = None
structured_analyzer = StructuredAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page."""
    return templates.TemplateResponse("index.html", {"request": request})

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    # Initialize PromptLayer
    initialize_promptlayer()
    
    # Initialize vector store
    initialize_vector_store()
    
    # Initialize the agent (this will be done on-demand, but we can test it here)
    try:
        global agent
        agent = ResumeReactAgent()
    except Exception as e:
        print(f"Failed to initialize agent: {str(e)}")
        # Continue anyway, we'll initialize on-demand

def get_agent():
    """Get or create the ReAct agent."""
    global agent
    if agent is None:
        agent = ResumeReactAgent()
    return agent

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Resume Analyzer API",
        "version": APP_VERSION,
        "docs": "/docs"
    }

@app.post("/analyze/text", response_model=Dict[str, Any])
async def analyze_resume_text(request: ResumeAnalysisRequest):
    """
    Analyze a resume from text input.
    
    Args:
        request: ResumeAnalysisRequest with resume_text and optional job_description
        
    Returns:
        Analysis results
    """
    # Start MLflow run
    with mlflow.start_run() as run:
        mlflow.log_param("resume_length", len(request.resume_text))
        mlflow.log_param("has_job_description", request.job_description is not None)
        
        start_time = time.time()
        
        try:
            # Get the agent
            agent = get_agent()
            
            # Execute the agent
            result = agent.analyze_resume(
                resume_text=request.resume_text,
                job_description=request.job_description
            )
            
            # Log metrics
            processing_time = time.time() - start_time
            mlflow.log_metric("processing_time_seconds", processing_time)
            mlflow.log_metric("success", 1)
            
            return result
            
        except Exception as e:
            # Log failure
            mlflow.log_metric("success", 0)
            mlflow.log_param("error", str(e))
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze resume: {str(e)}"
            )

@app.post("/analyze/file", response_model=Dict[str, Any])
async def analyze_resume_file(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """
    Analyze a resume from a file upload.
    
    Args:
        file: The resume file (PDF or DOCX)
        job_description: Optional job description for matching
        
    Returns:
        Analysis results
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Parse the resume based on file type
        resume_text = ""
        
        if file.filename.endswith(".pdf"):
            from pypdf import PdfReader
            from io import BytesIO
            reader = PdfReader(BytesIO(content))
            for page in reader.pages:
                resume_text += page.extract_text()
                
        elif file.filename.endswith(".docx"):
            import docx
            from io import BytesIO
            doc = docx.Document(BytesIO(content))
            resume_text = "\n".join([p.text for p in doc.paragraphs])
                
        else:
            # Assume it's plain text
            resume_text = content.decode("utf-8")
        
        # Get the agent
        agent = get_agent()
        
        # Execute the agent
        result = agent.analyze_resume(
            resume_text=resume_text,
            job_description=job_description
        )
        
        return result
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze resume: {str(e)}"
        )

@app.post("/simple_analyze", response_model=Dict[str, Any])
async def simple_analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """
    A simplified version of resume analysis that uses fewer API calls.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Parse the resume based on file type
        resume_text = ""
        
        if file.filename.endswith(".pdf"):
            from pypdf import PdfReader
            from io import BytesIO
            reader = PdfReader(BytesIO(content))
            for page in reader.pages:
                resume_text += page.extract_text()
                
        elif file.filename.endswith(".docx"):
            import docx
            from io import BytesIO
            doc = docx.Document(BytesIO(content))
            resume_text = "\n".join([p.text for p in doc.paragraphs])
                
        else:
            # Assume it's plain text
            resume_text = content.decode("utf-8")
        
        # Get the agent
        agent = get_agent()
        
        # Use the direct analyze method to avoid agent overhead
        result = agent.direct_analyze(
            resume_text=resume_text,
            job_description=job_description
        )
        
        return result
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze resume: {str(e)}"
        )

@app.post("/structured_analyze", response_model=Dict[str, Any])
async def structured_analyze(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """
    Analyze a resume with structured output that doesn't use API calls.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Parse the resume based on file type
        resume_text = ""
        
        if file.filename.endswith(".pdf"):
            from pypdf import PdfReader
            from io import BytesIO
            reader = PdfReader(BytesIO(content))
            for page in reader.pages:
                resume_text += page.extract_text()
                
        elif file.filename.endswith(".docx"):
            import docx
            from io import BytesIO
            doc = docx.Document(BytesIO(content))
            resume_text = "\n".join([p.text for p in doc.paragraphs])
                
        else:
            # Assume it's plain text
            resume_text = content.decode("utf-8")
        
        # Use the structured analyzer
        result = structured_analyzer.analyze_resume(
            resume_text=resume_text,
            job_description=job_description
        )
        
        return result
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze resume: {str(e)}"
        )