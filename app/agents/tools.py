"""
Custom tools for the Resume ReAct agent.
"""
from typing import List, Dict, Any
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from app.services.parser import extract_skills, extract_experience, extract_education
from app.services.analyzer import analyze_strengths_weaknesses, calculate_job_match, suggest_improvements
from app.services.vector_store import get_similar_skills, get_industry_standards
import re

class ExtractSkillsInput(BaseModel):
    """Input for the extract skills tool."""
    resume_text: str = Field(..., description="The text content of the resume")

class ExtractExperienceInput(BaseModel):
    """Input for the extract experience tool."""
    resume_text: str = Field(..., description="The text content of the resume")
    
class ExtractEducationInput(BaseModel):
    """Input for the extract education tool."""
    resume_text: str = Field(..., description="The text content of the resume")

class AnalyzeStrengthsWeaknessesInput(BaseModel):
    """Input for the analyze strengths and weaknesses tool."""
    skills: List[str] = Field(..., description="List of extracted skills")
    experience: List[Dict[str, Any]] = Field(..., description="List of extracted experiences")
    education: List[Dict[str, Any]] = Field(..., description="List of extracted education")

class CalculateJobMatchInput(BaseModel):
    """Input for the calculate job match tool."""
    skills: List[str] = Field(..., description="List of extracted skills")
    experience: List[Dict[str, Any]] = Field(..., description="List of extracted experiences")
    education: List[Dict[str, Any]] = Field(..., description="List of extracted education")
    job_description: str = Field(..., description="The job description text")

class SuggestImprovementsInput(BaseModel):
    """Input for the suggest improvements tool."""
    resume_text: str = Field(..., description="The text content of the resume")
    strengths: List[str] = Field(..., description="List of identified strengths")
    weaknesses: List[str] = Field(..., description="List of identified weaknesses")

class MatchSkillsInput(BaseModel):
    """Input for the match skills tool."""
    resume_text: str = Field(..., description="The text content of the resume")
    job_description_text: str = Field(..., description="The text content of the job description")

def match_skills_tool(resume_text: str, job_description_text: str) -> Dict[str, Any]:
    """
    Extracts skills from resume and job description, finds common skills,
    and calculates a matching percentage.
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description_text)

    # Ensure we have lists of strings
    if not isinstance(resume_skills, list):
        resume_skills_list = resume_skills.get("skills", []) if isinstance(resume_skills, dict) else []
    else:
        resume_skills_list = resume_skills

    if not isinstance(jd_skills, list):
        jd_skills_list = jd_skills.get("skills", []) if isinstance(jd_skills, dict) else []
    else:
        jd_skills_list = jd_skills
    
    # Clean and normalize skills - remove newlines, extra spaces, and normalize case
    def clean_skill(skill):
        if isinstance(skill, str):
            # Remove newlines, extra spaces, and common prefixes
            cleaned = re.sub(r'\n+', ' ', skill)  # Replace newlines with spaces
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with single space
            cleaned = cleaned.strip('- •').strip()  # Remove bullet points and dashes
            return cleaned.strip()
        return str(skill).strip()
    
    # Clean the skills lists
    resume_skills_cleaned = [clean_skill(skill) for skill in resume_skills_list if clean_skill(skill)]
    jd_skills_cleaned = [clean_skill(skill) for skill in jd_skills_list if clean_skill(skill)]
        
    # Normalize skills to lower case for case-insensitive matching
    resume_skills_set = set(skill.lower() for skill in resume_skills_cleaned if skill)
    jd_skills_set = set(skill.lower() for skill in jd_skills_cleaned if skill)

    # Find matched skills (keep original case for display)
    matched_skills = []
    for resume_skill in resume_skills_cleaned:
        for jd_skill in jd_skills_cleaned:
            if resume_skill.lower() == jd_skill.lower():
                matched_skills.append(resume_skill)
                break
    
    # Remove duplicates while preserving order
    matched_skills = list(dict.fromkeys(matched_skills))
    
    # Calculate match percentage based on job description requirements
    if not jd_skills_set:
        match_percentage = 0.0
    else:
        match_percentage = (len(set(skill.lower() for skill in matched_skills)) / len(jd_skills_set)) * 100

    return {
        "matched_skills": matched_skills,
        "resume_skills": resume_skills_cleaned,
        "job_description_skills": jd_skills_cleaned,
        "match_percentage": round(match_percentage, 2)
    }

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
        Tool.from_function(
            func=match_skills_tool,
            name="MatchSkills",
            description="Matches skills between a resume and a job description, providing a match percentage.",
            args_schema=MatchSkillsInput,
            return_direct=False,
        )
    ]
    
    return tools