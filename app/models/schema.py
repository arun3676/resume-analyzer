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

class InterviewQuestionRequest(BaseModel):
    """Request model for generating interview questions."""
    resume_text: str
    job_description: str
    question_types: Optional[List[str]] = Field(default_factory=lambda: ["technical", "behavioral", "situational"])
    num_questions: Optional[int] = 5

class InterviewQuestion(BaseModel):
    """Model for a single interview question."""
    question: str
    type: str # e.g., "technical", "behavioral", "situational"
    expected_answer_format: Optional[str] = None # e.g., "STAR method"

class InterviewQuestionsResponse(BaseModel):
    """Response model for generated interview questions."""
    questions: List[InterviewQuestion]

class MockInterviewFeedbackRequest(BaseModel):
    """Request model for mock interview feedback."""
    question: str
    user_answer: str
    job_description: Optional[str] = None # For context

class MockInterviewFeedbackResponse(BaseModel):
    """Response model for mock interview feedback."""
    feedback: str
    score: Optional[float] = None # Overall score, e.g., 0.0 to 1.0
    suggestions_for_improvement: Optional[List[str]] = None

class SalaryIntelligenceRequest(BaseModel):
    """Request model for salary intelligence analysis."""
    resume_text: str
    job_title: str
    location: str
    years_of_experience: Optional[int] = None
    company_size: Optional[str] = None # e.g., "startup", "small", "medium", "large", "enterprise"
    industry: Optional[str] = None

class SalaryRange(BaseModel):
    """Model for salary range information."""
    min_salary: float
    max_salary: float
    median_salary: float
    currency: str = "USD"

class MarketPositioning(BaseModel):
    """Model for market positioning analysis."""
    percentile: float # e.g., 75.5 means top 25% of candidates
    positioning_text: str # e.g., "You're in the top 25% for your role"
    comparison_factors: List[str] # Factors that contribute to positioning

class NegotiationStrategy(BaseModel):
    """Model for salary negotiation strategies."""
    strategy_type: str # e.g., "aggressive", "moderate", "conservative"
    key_points: List[str]
    timing_advice: str
    leverage_factors: List[str]

class SalaryIntelligenceResponse(BaseModel):
    """Response model for salary intelligence analysis."""
    predicted_salary_range: SalaryRange
    market_positioning: MarketPositioning
    negotiation_strategies: List[NegotiationStrategy]
    skill_value_analysis: Dict[str, float] # skill -> market value impact
    location_adjustment: float # percentage adjustment for location
    experience_premium: float # percentage premium for experience level
    recommendations: List[str]
    data_confidence: float # 0.0 to 1.0, confidence in the prediction