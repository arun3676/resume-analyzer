from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date

class LearningResource(BaseModel):
    name: str
    url: str
    platform: Optional[str] = None # e.g., Coursera, Udemy, YouTube, Article
    type: Optional[str] = None # e.g., Course, Tutorial, Documentation
    estimated_duration: Optional[str] = None # e.g., "10 hours", "3 weeks"

class Skill(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    learning_resources: Optional[List[LearningResource]] = []
    # Consider adding category, proficiency_levels, etc. later

class CareerStage(BaseModel):
    name: str
    description: Optional[str] = None
    skills_required: List[str] # List of Skill IDs
    # Could also include estimated_time_to_master_skills, resources, etc.

class CareerPath(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    stages: List[CareerStage]
    # Could include entry_level_skills, average_salary_range, etc.

# New models for Career Trajectory Visualization

class SkillMilestone(BaseModel):
    skill_id: str
    skill_name: str
    proficiency_level: int  # 1-5 scale (1=Beginner, 5=Expert)
    achieved_date: Optional[date] = None
    target_date: Optional[date] = None
    estimated_learning_time_weeks: int = 4  # Default to 4 weeks
    difficulty_level: str = "Intermediate"  # Beginner, Intermediate, Advanced

class CareerStageEvolution(BaseModel):
    stage_name: str
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    estimated_duration_months: int = 6  # Default duration
    skill_milestones: List[SkillMilestone]
    completion_percentage: float = 0.0
    status: str = "Not Started"  # Not Started, In Progress, Completed

class IndustryTransition(BaseModel):
    from_industry: str
    to_industry: str
    required_skills: List[str]  # Skill IDs needed for transition
    transition_difficulty: str = "Medium"  # Easy, Medium, Hard
    estimated_transition_time_months: int = 12
    common_transition_roles: List[str] = []
    success_rate: float = 0.75  # 0.0 to 1.0

class CareerTrajectory(BaseModel):
    id: str
    user_id: Optional[str] = None  # For personalized trajectories
    current_stage: str
    target_career_path_id: str
    target_stage: str
    start_date: date
    target_completion_date: date
    stage_evolutions: List[CareerStageEvolution]
    current_skills: List[str]  # Current skill IDs
    skill_milestones: List[SkillMilestone]
    industry_transitions: Optional[List[IndustryTransition]] = []
    
class SkillEvolution(BaseModel):
    skill_id: str
    skill_name: str
    historical_levels: List[Dict[str, Any]]  # [{"date": "2024-01", "level": 3}, ...]
    projected_levels: List[Dict[str, Any]]   # Future projections
    learning_velocity: float = 1.0  # Skills per month learning rate
    mastery_prediction_date: Optional[date] = None

class CareerGrowthPattern(BaseModel):
    pattern_id: str
    pattern_name: str
    description: str
    typical_progression: List[str]  # List of role names in order
    average_timeframes: List[int]   # Months between each progression
    required_skill_combinations: List[List[str]]  # Skills needed at each stage
    industry_applicability: List[str]  # Which industries this pattern applies to
    success_indicators: List[str]  # Key metrics for successful progression

# Example of how related_skills or next_stages could be done if we want a graph structure later:
# class Skill(BaseModel):
#     id: str
#     name: str
#     description: Optional[str] = None
#     related_skills: List[str] = [] # List of Skill IDs

# class CareerStage(BaseModel):
#     name: str
#     description: Optional[str] = None
#     skills_required: List[str] # List of Skill IDs
#     next_stages: List[str] = [] # List of CareerStage names or IDs within the same path or other paths 