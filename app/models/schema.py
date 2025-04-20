"""
Data models and schemas for the Resume Analyzer.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ResumeAnalysisRequest(BaseModel):
    """Request model for resume analysis."""
    resume_text: str 
    job_description: Optional[str] = None
    
    class Config:
        json_encoders = {
            str: lambda v: v.replace('\t', ' ').replace('\r', '')
        }
class SkillInfo(BaseModel):
    """Model for skill information."""
    name: str
    category: Optional[str] = None

class ExperienceInfo(BaseModel):
    """Model for work experience information."""
    company: str
    title: str
    dates: str
    description: Optional[str] = None

class EducationInfo(BaseModel):
    """Model for education information."""
    degree: str
    institution: str
    dates: str
    field_of_study: Optional[str] = None

class StrengthsWeaknesses(BaseModel):
    """Model for strengths and weaknesses analysis."""
    strengths: List[str]
    weaknesses: List[str]

class JobMatch(BaseModel):
    """Model for job match analysis."""
    overall_match_percent: float
    skill_match_percent: float
    experience_match_percent: float
    education_match_percent: float
    matching_skills: List[str]
    missing_skills: List[str]

class ImprovementSuggestions(BaseModel):
    """Model for improvement suggestions."""
    suggestions: List[str]

class ResumeAnalysisResponse(BaseModel):
    """Response model for resume analysis."""
    skills: List[SkillInfo]
    experience: List[ExperienceInfo]
    education: List[EducationInfo]
    analysis: StrengthsWeaknesses
    job_match: Optional[JobMatch] = None
    improvements: ImprovementSuggestions
    summary: str