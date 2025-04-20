"""
Custom tools for the Resume ReAct agent.
"""
from typing import List, Dict, Any
from langchain.tools import Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel as PydanticBaseModel

from app.services.parser import extract_skills, extract_experience, extract_education
from app.services.analyzer import analyze_strengths_weaknesses, calculate_job_match, suggest_improvements
from app.services.vector_store import get_similar_skills, get_industry_standards

class ExtractSkillsInput(PydanticBaseModel):
    """Input for the extract skills tool."""
    resume_text: str = Field(..., description="The text content of the resume")

class ExtractExperienceInput(PydanticBaseModel):
    """Input for the extract experience tool."""
    resume_text: str = Field(..., description="The text content of the resume")
    
class ExtractEducationInput(PydanticBaseModel):
    """Input for the extract education tool."""
    resume_text: str = Field(..., description="The text content of the resume")

class AnalyzeStrengthsWeaknessesInput(PydanticBaseModel):
    """Input for the analyze strengths and weaknesses tool."""
    skills: List[str] = Field(..., description="List of extracted skills")
    experience: List[Dict[str, Any]] = Field(..., description="List of extracted experiences")
    education: List[Dict[str, Any]] = Field(..., description="List of extracted education")

class CalculateJobMatchInput(PydanticBaseModel):
    """Input for the calculate job match tool."""
    skills: List[str] = Field(..., description="List of extracted skills")
    experience: List[Dict[str, Any]] = Field(..., description="List of extracted experiences")
    education: List[Dict[str, Any]] = Field(..., description="List of extracted education")
    job_description: str = Field(..., description="The job description text")

class SuggestImprovementsInput(PydanticBaseModel):
    """Input for the suggest improvements tool."""
    resume_text: str = Field(..., description="The text content of the resume")
    strengths: List[str] = Field(..., description="List of identified strengths")
    weaknesses: List[str] = Field(..., description="List of identified weaknesses")

def get_resume_tools() -> List[Tool]:
    """
    Get the custom tools for resume analysis using the ReAct framework.
    
    Returns:
        List of tools for the agent to use
    """
    tools = [
        Tool.from_function(
            func=extract_skills,
            name="ExtractSkills",
            description="Extract a list of skills from the resume text",
            args_schema=ExtractSkillsInput,
            return_direct=False,
        ),
        Tool.from_function(
            func=extract_experience,
            name="ExtractExperience",
            description="Extract work experience details from the resume text",
            args_schema=ExtractExperienceInput,
            return_direct=False,
        ),
        Tool.from_function(
            func=extract_education,
            name="ExtractEducation",
            description="Extract education details from the resume text",
            args_schema=ExtractEducationInput,
            return_direct=False,
        ),
        Tool.from_function(
            func=analyze_strengths_weaknesses,
            name="AnalyzeStrengthsWeaknesses",
            description="Analyze the strengths and weaknesses based on skills, experience, and education",
            args_schema=AnalyzeStrengthsWeaknessesInput,
            return_direct=False,
        ),
        Tool.from_function(
            func=calculate_job_match,
            name="CalculateJobMatch",
            description="Calculate how well the resume matches a job description",
            args_schema=CalculateJobMatchInput,
            return_direct=False,
        ),
        Tool.from_function(
            func=suggest_improvements,
            name="SuggestImprovements",
            description="Suggest improvements for the resume based on strengths and weaknesses",
            args_schema=SuggestImprovementsInput,
            return_direct=False,
        ),
        Tool.from_function(
            func=get_similar_skills,
            name="GetSimilarSkills",
            description="Find similar or related skills that could enhance the resume",
            return_direct=False,
        ),
        Tool.from_function(
            func=get_industry_standards,
            name="GetIndustryStandards",
            description="Get industry standards for resumes in a specific field",
            return_direct=False,
        ),
    ]
    
    return tools