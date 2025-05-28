from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
from datetime import datetime, date, timedelta
import random

from app.models.skills_career import (
    Skill, CareerPath, CareerStage, LearningResource,
    SkillMilestone, CareerStageEvolution, IndustryTransition, 
    CareerTrajectory, SkillEvolution, CareerGrowthPattern
)

router = APIRouter()

# --- Request/Response Models for Skills Gap Analysis ---
class SkillsGapRequest(BaseModel):
    current_skill_ids: List[str]
    target_career_path_id: str
    target_stage_name: str

class MissingSkill(Skill):
    pass

class SkillsGapResponse(BaseModel):
    target_career_path_id: str
    target_stage_name: str
    current_skills: List[Skill]
    required_skills_for_stage: List[Skill]
    missing_skills: List[MissingSkill]
    all_skills_met: bool

class ExtractSkillsRequest(BaseModel):
    resume_text: str

class ExtractSkillsResponse(BaseModel):
    success: bool
    skill_ids: List[str]
    extracted_skill_names: List[str] # The original names found
    message: Optional[str] = None

class IntelligentRecommendationRequest(BaseModel):
    resume_text: str
    current_skill_ids: List[str]

class ResumeAnalysis(BaseModel):
    detected_roles: List[str]
    industry_indicators: List[str]
    experience_level: str
    role_keywords: List[str]
    confidence_score: float

class IntelligentRecommendation(BaseModel):
    career_path: CareerPath
    stages_match: List[dict]
    overall_match_percentage: float
    relevance_score: float
    confidence_level: str
    why_recommended: str
    resume_analysis: ResumeAnalysis

# --- New Request/Response Models for Career Trajectory ---
class GenerateTrajectoryRequest(BaseModel):
    current_skill_ids: List[str]
    target_career_path_id: str
    target_stage_name: Optional[str] = None  # If None, aims for the final stage
    start_date: Optional[date] = None
    user_experience_level: str = "mid"  # junior, mid, senior

class SkillEvolutionRequest(BaseModel):
    skill_ids: List[str]
    timeline_months: int = 24  # How far to project into the future

class IndustryTransitionRequest(BaseModel):
    current_industry: str
    target_industry: str
    current_skills: List[str]

# --- Sample Data Store ---
# In a real application, this would come from a database.

SKILLS_DB: List[Skill] = [
    Skill(
        id="python", 
        name="Python", 
        description="General-purpose programming language",
        learning_resources=[
            LearningResource(name="Python for Everybody", url="https://www.coursera.org/specializations/python", platform="Coursera", type="Specialization"),
            LearningResource(name="Official Python Tutorial", url="https://docs.python.org/3/tutorial/", platform="Python.org", type="Documentation")
        ]
    ),
    Skill(
        id="fastapi", 
        name="FastAPI", 
        description="Modern, fast web framework for building APIs",
        learning_resources=[
            LearningResource(name="FastAPI Official Documentation", url="https://fastapi.tiangolo.com/", platform="Tiangolo", type="Documentation"),
            LearningResource(name="Full Stack FastAPI and React", url="https://www.udemy.com/course/full-stack-fastapi-react/", platform="Udemy", type="Course")
        ]
    ),
    Skill(
        id="sql", 
        name="SQL", 
        description="Standard language for managing relational databases",
        learning_resources=[
            LearningResource(name="SQL for Data Science", url="https://www.coursera.org/learn/sql-for-data-science", platform="Coursera", type="Course"),
            LearningResource(name="SQLZoo", url="https://sqlzoo.net/", platform="SQLZoo", type="Interactive Tutorial")
        ]
    ),
    Skill(id="communication", name="Communication", description="Effective communication and interpersonal skills"),
    Skill(id="problem_solving", name="Problem Solving", description="Analytical and problem-solving abilities"),
    Skill(id="project_management", name="Project Management", description="Planning, executing, and overseeing projects"),
    Skill(
        id="data_analysis", 
        name="Data Analysis", 
        description="Interpreting data to inform business decisions",
        learning_resources=[
            LearningResource(name="Google Data Analytics Professional Certificate", url="https://www.coursera.org/professional-certificates/google-data-analytics", platform="Coursera", type="Professional Certificate")
        ]
    ),
    Skill(
        id="machine_learning", 
        name="Machine Learning", 
        description="Developing algorithms that allow systems to learn from data",
        learning_resources=[
            LearningResource(name="Machine Learning by Andrew Ng", url="https://www.coursera.org/learn/machine-learning", platform="Coursera", type="Course"),
            LearningResource(name="Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow", url="https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/", platform="O'Reilly", type="Book")
        ]
    ),
    Skill(id="cloud_computing", name="Cloud Computing", description="Delivering computing services over the internet (e.g., AWS, Azure, GCP)"),
    Skill(id="devops", name="DevOps", description="Practices that combine software development and IT operations"),
    # New skills for expanded career paths
    Skill(
        id="javascript", 
        name="JavaScript", 
        description="Programming language for web development",
        learning_resources=[
            LearningResource(name="JavaScript: The Complete Guide", url="https://www.udemy.com/course/javascript-the-complete-guide-2020-beginner-advanced/", platform="Udemy", type="Course"),
            LearningResource(name="MDN JavaScript Guide", url="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", platform="MDN", type="Documentation")
        ]
    ),
    Skill(
        id="react", 
        name="React", 
        description="JavaScript library for building user interfaces",
        learning_resources=[
            LearningResource(name="React - The Complete Guide", url="https://www.udemy.com/course/react-the-complete-guide-incl-redux/", platform="Udemy", type="Course"),
            LearningResource(name="Official React Tutorial", url="https://reactjs.org/tutorial/tutorial.html", platform="React.org", type="Documentation")
        ]
    ),
    Skill(
        id="html_css", 
        name="HTML/CSS", 
        description="Markup and styling languages for web development",
        learning_resources=[
            LearningResource(name="HTML & CSS Crash Course", url="https://www.youtube.com/watch?v=UB1O30fR-EE", platform="YouTube", type="Video Course"),
            LearningResource(name="CSS Grid and Flexbox", url="https://www.udemy.com/course/css-grid-flexbox/", platform="Udemy", type="Course")
        ]
    ),
    Skill(
        id="docker", 
        name="Docker", 
        description="Containerization platform for application deployment",
        learning_resources=[
            LearningResource(name="Docker Mastery", url="https://www.udemy.com/course/docker-mastery/", platform="Udemy", type="Course"),
            LearningResource(name="Official Docker Documentation", url="https://docs.docker.com/", platform="Docker", type="Documentation")
        ]
    ),
    Skill(
        id="kubernetes", 
        name="Kubernetes", 
        description="Container orchestration platform",
        learning_resources=[
            LearningResource(name="Kubernetes for Developers", url="https://www.udemy.com/course/kubernetes-for-developers/", platform="Udemy", type="Course"),
            LearningResource(name="Kubernetes Official Tutorials", url="https://kubernetes.io/docs/tutorials/", platform="Kubernetes.io", type="Documentation")
        ]
    ),
    Skill(
        id="aws", 
        name="AWS", 
        description="Amazon Web Services cloud platform",
        learning_resources=[
            LearningResource(name="AWS Certified Solutions Architect", url="https://www.udemy.com/course/aws-certified-solutions-architect-associate/", platform="Udemy", type="Course"),
            LearningResource(name="AWS Free Tier", url="https://aws.amazon.com/free/", platform="AWS", type="Hands-on")
        ]
    ),
    Skill(
        id="product_strategy", 
        name="Product Strategy", 
        description="Planning and executing product roadmaps",
        learning_resources=[
            LearningResource(name="Product Management Fundamentals", url="https://www.coursera.org/learn/product-management-fundamentals", platform="Coursera", type="Course")
        ]
    ),
    Skill(
        id="user_research", 
        name="User Research", 
        description="Understanding user needs and behaviors",
        learning_resources=[
            LearningResource(name="User Experience Research and Design", url="https://www.coursera.org/specializations/michiganux", platform="Coursera", type="Specialization")
        ]
    ),
    Skill(
        id="ui_ux_design", 
        name="UI/UX Design", 
        description="User interface and user experience design",
        learning_resources=[
            LearningResource(name="Google UX Design Certificate", url="https://www.coursera.org/professional-certificates/google-ux-design", platform="Coursera", type="Professional Certificate"),
            LearningResource(name="Figma for Beginners", url="https://www.figma.com/academy/", platform="Figma", type="Tutorial")
        ]
    ),
    Skill(
        id="agile_scrum", 
        name="Agile/Scrum", 
        description="Agile project management methodologies",
        learning_resources=[
            LearningResource(name="Certified ScrumMaster", url="https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster", platform="Scrum Alliance", type="Certification")
        ]
    ),
    Skill(
        id="git", 
        name="Git", 
        description="Version control system for tracking code changes",
        learning_resources=[
            LearningResource(name="Git Complete Guide", url="https://www.udemy.com/course/git-complete/", platform="Udemy", type="Course"),
            LearningResource(name="Pro Git Book", url="https://git-scm.com/book", platform="Git-SCM", type="Book")
        ]
    ),
    Skill(
        id="ci_cd", 
        name="CI/CD", 
        description="Continuous Integration and Continuous Deployment",
        learning_resources=[
            LearningResource(name="Jenkins Complete Guide", url="https://www.udemy.com/course/jenkins-from-zero-to-hero/", platform="Udemy", type="Course")
        ]
    ),
    Skill(
        id="monitoring", 
        name="Monitoring & Observability", 
        description="System monitoring and performance tracking",
        learning_resources=[
            LearningResource(name="Prometheus and Grafana", url="https://www.udemy.com/course/prometheus-course/", platform="Udemy", type="Course")
        ]
    ),
    Skill(
        id="stakeholder_management", 
        name="Stakeholder Management", 
        description="Managing relationships with project stakeholders",
        learning_resources=[
            LearningResource(name="Stakeholder Management Course", url="https://www.coursera.org/learn/stakeholder-management", platform="Coursera", type="Course")
        ]
    ),
    Skill(
        id="data_visualization", 
        name="Data Visualization", 
        description="Creating visual representations of data",
        learning_resources=[
            LearningResource(name="Tableau Fundamentals", url="https://www.tableau.com/learn/training", platform="Tableau", type="Training")
        ]
    )
]

CAREER_PATHS_DB: List[CareerPath] = [
    CareerPath(
        id="swe_backend",
        name="Backend Software Engineer Path",
        description="Focuses on server-side logic, databases, and APIs.",
        stages=[
            CareerStage(
                name="Junior Backend Developer",
                skills_required=["python", "sql", "problem_solving", "git"]
            ),
            CareerStage(
                name="Backend Developer",
                skills_required=["python", "fastapi", "sql", "communication", "devops", "git"]
            ),
            CareerStage(
                name="Senior Backend Developer / Tech Lead",
                skills_required=["python", "fastapi", "sql", "project_management", "cloud_computing", "machine_learning", "git", "ci_cd"]
            )
        ]
    ),
    CareerPath(
        id="swe_frontend",
        name="Frontend Software Engineer Path",
        description="Focuses on user interfaces, web technologies, and user experience.",
        stages=[
            CareerStage(
                name="Junior Frontend Developer",
                skills_required=["html_css", "javascript", "problem_solving", "git"]
            ),
            CareerStage(
                name="Frontend Developer",
                skills_required=["html_css", "javascript", "react", "communication", "git", "ui_ux_design"]
            ),
            CareerStage(
                name="Senior Frontend Developer / Tech Lead",
                skills_required=["html_css", "javascript", "react", "project_management", "ui_ux_design", "git", "ci_cd", "communication"]
            )
        ]
    ),
    CareerPath(
        id="swe_fullstack",
        name="Full Stack Software Engineer Path",
        description="Combines both frontend and backend development skills.",
        stages=[
            CareerStage(
                name="Junior Full Stack Developer",
                skills_required=["html_css", "javascript", "python", "sql", "problem_solving", "git"]
            ),
            CareerStage(
                name="Full Stack Developer",
                skills_required=["html_css", "javascript", "react", "python", "fastapi", "sql", "communication", "git"]
            ),
            CareerStage(
                name="Senior Full Stack Developer / Tech Lead",
                skills_required=["html_css", "javascript", "react", "python", "fastapi", "sql", "project_management", "cloud_computing", "devops", "git", "ci_cd"]
            )
        ]
    ),
    CareerPath(
        id="devops_engineer",
        name="DevOps Engineer Path",
        description="Focuses on infrastructure, automation, and deployment pipelines.",
        stages=[
            CareerStage(
                name="Junior DevOps Engineer",
                skills_required=["git", "docker", "problem_solving", "communication"]
            ),
            CareerStage(
                name="DevOps Engineer",
                skills_required=["git", "docker", "kubernetes", "aws", "ci_cd", "monitoring", "communication"]
            ),
            CareerStage(
                name="Senior DevOps Engineer / Platform Lead",
                skills_required=["git", "docker", "kubernetes", "aws", "ci_cd", "monitoring", "project_management", "cloud_computing", "devops"]
            )
        ]
    ),
    CareerPath(
        id="product_manager",
        name="Product Manager Path",
        description="Focuses on product strategy, user research, and cross-functional collaboration.",
        stages=[
            CareerStage(
                name="Associate Product Manager",
                skills_required=["communication", "problem_solving", "user_research", "data_analysis"]
            ),
            CareerStage(
                name="Product Manager",
                skills_required=["communication", "problem_solving", "user_research", "data_analysis", "product_strategy", "agile_scrum", "stakeholder_management"]
            ),
            CareerStage(
                name="Senior Product Manager / Product Lead",
                skills_required=["communication", "problem_solving", "user_research", "data_analysis", "product_strategy", "agile_scrum", "stakeholder_management", "project_management"]
            )
        ]
    ),
    CareerPath(
        id="ux_designer",
        name="UX Designer Path",
        description="Focuses on user experience design, research, and interface design.",
        stages=[
            CareerStage(
                name="Junior UX Designer",
                skills_required=["ui_ux_design", "user_research", "communication", "problem_solving"]
            ),
            CareerStage(
                name="UX Designer",
                skills_required=["ui_ux_design", "user_research", "communication", "problem_solving", "data_analysis", "stakeholder_management"]
            ),
            CareerStage(
                name="Senior UX Designer / Design Lead",
                skills_required=["ui_ux_design", "user_research", "communication", "problem_solving", "data_analysis", "stakeholder_management", "project_management"]
            )
        ]
    ),
    CareerPath(
        id="data_analyst",
        name="Data Analyst Path",
        description="Focuses on collecting, processing, and performing statistical analyses of data.",
        stages=[
            CareerStage(
                name="Junior Data Analyst",
                skills_required=["sql", "python", "data_analysis", "communication"]
            ),
            CareerStage(
                name="Data Analyst",
                skills_required=["sql", "python", "data_analysis", "problem_solving", "project_management", "data_visualization"]
            ),
            CareerStage(
                name="Senior Data Analyst / Data Scientist",
                skills_required=["sql", "python", "machine_learning", "data_analysis", "cloud_computing", "data_visualization", "communication"]
            )
        ]
    )
]

# --- Sample Data for Industry Transitions ---
INDUSTRY_TRANSITIONS_DB = [
    IndustryTransition(
        from_industry="finance",
        to_industry="tech",
        required_skills=["python", "sql", "data_analysis", "cloud_computing"],
        transition_difficulty="Medium",
        estimated_transition_time_months=8,
        common_transition_roles=["FinTech Developer", "Data Analyst", "Backend Engineer"],
        success_rate=0.78
    ),
    IndustryTransition(
        from_industry="marketing",
        to_industry="tech",
        required_skills=["data_analysis", "product_strategy", "user_research", "sql"],
        transition_difficulty="Easy",
        estimated_transition_time_months=6,
        common_transition_roles=["Product Manager", "UX Researcher", "Growth Analyst"],
        success_rate=0.85
    ),
    IndustryTransition(
        from_industry="consulting", 
        to_industry="tech",
        required_skills=["project_management", "data_analysis", "product_strategy", "stakeholder_management"],
        transition_difficulty="Easy",
        estimated_transition_time_months=4,
        common_transition_roles=["Product Manager", "Program Manager", "Business Analyst"],
        success_rate=0.92
    ),
    IndustryTransition(
        from_industry="healthcare",
        to_industry="tech",
        required_skills=["data_analysis", "python", "machine_learning", "sql"],
        transition_difficulty="Hard",
        estimated_transition_time_months=12,
        common_transition_roles=["Health Tech Developer", "Medical Data Scientist", "Healthcare Product Manager"],
        success_rate=0.65
    )
]

# --- Sample Career Growth Patterns ---
CAREER_GROWTH_PATTERNS_DB = [
    CareerGrowthPattern(
        pattern_id="tech_individual_contributor",
        pattern_name="Technical Individual Contributor Path",
        description="Focus on deep technical skills and expertise",
        typical_progression=["Junior Developer", "Developer", "Senior Developer", "Staff Engineer", "Principal Engineer"],
        average_timeframes=[12, 18, 24, 36, 48],  # months between progressions
        required_skill_combinations=[
            ["git", "problem_solving"],
            ["python", "sql", "git", "communication"],
            ["python", "fastapi", "sql", "cloud_computing", "git", "ci_cd"],
            ["python", "fastapi", "sql", "cloud_computing", "machine_learning", "project_management"],
            ["python", "fastapi", "sql", "cloud_computing", "machine_learning", "project_management", "stakeholder_management"]
        ],
        industry_applicability=["tech", "finance", "healthcare", "ecommerce"],
        success_indicators=["Technical depth", "Code quality", "System design skills", "Mentoring junior developers"]
    ),
    CareerGrowthPattern(
        pattern_id="tech_management",
        pattern_name="Engineering Management Path",
        description="Transition from individual contributor to people management",
        typical_progression=["Senior Developer", "Tech Lead", "Engineering Manager", "Senior Engineering Manager", "Director of Engineering"],
        average_timeframes=[18, 12, 24, 36, 48],
        required_skill_combinations=[
            ["python", "fastapi", "sql", "cloud_computing", "project_management"],
            ["python", "project_management", "communication", "stakeholder_management"],
            ["project_management", "communication", "stakeholder_management", "agile_scrum"],
            ["project_management", "communication", "stakeholder_management", "agile_scrum", "product_strategy"],
            ["project_management", "communication", "stakeholder_management", "product_strategy"]
        ],
        industry_applicability=["tech", "finance", "healthcare"],
        success_indicators=["Team performance", "People development", "Strategic thinking", "Cross-functional collaboration"]
    ),
    CareerGrowthPattern(
        pattern_id="product_management",
        pattern_name="Product Management Career Path",
        description="Focus on product strategy and user-centric development",
        typical_progression=["Associate PM", "Product Manager", "Senior PM", "Principal PM", "VP of Product"],
        average_timeframes=[12, 18, 24, 36, 60],
        required_skill_combinations=[
            ["communication", "user_research", "data_analysis"],
            ["communication", "user_research", "data_analysis", "product_strategy", "agile_scrum"],
            ["product_strategy", "stakeholder_management", "data_analysis", "user_research", "project_management"],
            ["product_strategy", "stakeholder_management", "data_analysis", "project_management"],
            ["product_strategy", "stakeholder_management", "project_management"]
        ],
        industry_applicability=["tech", "ecommerce", "finance", "healthcare"],
        success_indicators=["Product success metrics", "User satisfaction", "Strategic vision", "Market understanding"]
    )
]

# Helper function to get skill details by ID
def get_skill_by_id(skill_id: str) -> Optional[Skill]:
    for skill in SKILLS_DB:
        if skill.id == skill_id:
            return skill
    return None

def analyze_resume_context(resume_text: str) -> ResumeAnalysis:
    """
    Analyze resume text to extract job roles, industry, experience level, and other context
    """
    resume_lower = resume_text.lower()
    
    # Define role patterns and keywords
    role_patterns = {
        'backend_engineer': [
            r'\b(?:backend|back-end|server-side)\s*(?:developer|engineer|programmer)\b',
            r'\bapi\s*developer\b',
            r'\b(?:python|java|node\.?js|php|golang|rust)\s*developer\b',
            r'\bdatabase\s*(?:developer|administrator|engineer)\b'
        ],
        'frontend_engineer': [
            r'\b(?:frontend|front-end|ui|user\s*interface)\s*(?:developer|engineer|programmer)\b',
            r'\b(?:react|angular|vue|javascript|typescript)\s*developer\b',
            r'\bweb\s*developer\b',
            r'\b(?:html|css|javascript)\s*developer\b'
        ],
        'fullstack_engineer': [
            r'\b(?:fullstack|full-stack|full\s*stack)\s*(?:developer|engineer|programmer)\b',
            r'\bfull\s*stack\s*developer\b'
        ],
        'devops_engineer': [
            r'\b(?:devops|dev-ops|site\s*reliability|sre)\s*(?:engineer|specialist|administrator)\b',
            r'\b(?:infrastructure|deployment|automation)\s*engineer\b',
            r'\b(?:docker|kubernetes|aws|azure|gcp|cloud)\s*engineer\b',
            r'\bplatform\s*engineer\b',
            r'\bsystem\s*administrator\b'
        ],
        'data_analyst': [
            r'\bdata\s*(?:analyst|scientist|engineer)\b',
            r'\bbusiness\s*(?:analyst|intelligence)\b',
            r'\b(?:sql|database|analytics)\s*(?:analyst|specialist)\b',
            r'\bmachine\s*learning\s*engineer\b'
        ],
        'product_manager': [
            r'\bproduct\s*(?:manager|owner|lead)\b',
            r'\bproject\s*manager\b',
            r'\bprogram\s*manager\b'
        ],
        'ux_designer': [
            r'\b(?:ux|ui|user\s*experience|user\s*interface)\s*(?:designer|researcher)\b',
            r'\bdesign\s*(?:lead|manager|director)\b',
            r'\bproduct\s*designer\b'
        ]
    }
    
    # Industry indicators
    industry_indicators = {
        'tech': ['startup', 'saas', 'software company', 'tech company', 'technology', 'fintech', 'edtech'],
        'finance': ['bank', 'financial services', 'investment', 'trading', 'fintech', 'insurance'],
        'healthcare': ['hospital', 'healthcare', 'medical', 'pharma', 'biotech', 'health tech'],
        'ecommerce': ['e-commerce', 'ecommerce', 'retail', 'marketplace', 'shopping'],
        'consulting': ['consulting', 'advisory', 'professional services'],
        'enterprise': ['enterprise', 'corporation', 'fortune 500', 'large company']
    }
    
    # Experience level indicators
    experience_patterns = {
        'senior': [r'\bsenior\b', r'\blead\b', r'\bprincipal\b', r'\bstaff\b', r'\barchitect\b', r'\bmanager\b', r'\bdirector\b'],
        'mid': [r'\b(?:mid|middle)\s*level\b', r'\b\d+\+?\s*years?\s*(?:of\s*)?experience\b'],
        'junior': [r'\bjunior\b', r'\bentry\s*level\b', r'\bintern\b', r'\bassociate\b', r'\bgraduate\b']
    }
    
    detected_roles = []
    role_keywords = []
    
    # Detect roles
    for role_type, patterns in role_patterns.items():
        for pattern in patterns:
            if re.search(pattern, resume_lower):
                if role_type not in detected_roles:
                    detected_roles.append(role_type)
                matches = re.findall(pattern, resume_lower)
                role_keywords.extend(matches)
    
    # Detect industry
    detected_industries = []
    for industry, keywords in industry_indicators.items():
        for keyword in keywords:
            if keyword in resume_lower:
                if industry not in detected_industries:
                    detected_industries.append(industry)
    
    # Detect experience level
    experience_level = 'mid'  # default
    for level, patterns in experience_patterns.items():
        for pattern in patterns:
            if re.search(pattern, resume_lower):
                experience_level = level
                break
        if experience_level != 'mid':
            break
    
    # Calculate confidence score based on how many indicators we found
    confidence_factors = [
        len(detected_roles) > 0,
        len(detected_industries) > 0,
        len(role_keywords) > 0,
        experience_level != 'mid'
    ]
    confidence_score = sum(confidence_factors) / len(confidence_factors)
    
    return ResumeAnalysis(
        detected_roles=detected_roles,
        industry_indicators=detected_industries,
        experience_level=experience_level,
        role_keywords=role_keywords,
        confidence_score=confidence_score
    )

def calculate_relevance_score(career_path_id: str, resume_analysis: ResumeAnalysis, skill_match_percentage: float) -> tuple[float, str]:
    """
    Calculate how relevant a career path is based on resume analysis
    Returns (relevance_score, explanation)
    """
    relevance_score = 0.0
    explanations = []
    
    # Map career path IDs to role types
    path_role_mapping = {
        'swe_backend': 'backend_engineer',
        'swe_frontend': 'frontend_engineer', 
        'swe_fullstack': 'fullstack_engineer',
        'devops_engineer': 'devops_engineer',
        'data_analyst': 'data_analyst',
        'product_manager': 'product_manager',
        'ux_designer': 'ux_designer'
    }
    
    mapped_role = path_role_mapping.get(career_path_id)
    
    # Direct role match (highest weight)
    if mapped_role in resume_analysis.detected_roles:
        relevance_score += 40
        explanations.append(f"Direct role match found in resume")
    
    # Related role matches
    related_roles = {
        'swe_backend': ['devops_engineer', 'fullstack_engineer'],
        'swe_frontend': ['fullstack_engineer', 'ux_designer'],
        'swe_fullstack': ['backend_engineer', 'frontend_engineer'],
        'devops_engineer': ['backend_engineer'],
        'data_analyst': ['backend_engineer'],
        'product_manager': ['ux_designer'],
        'ux_designer': ['frontend_engineer', 'product_manager']
    }
    
    if career_path_id in related_roles:
        for related_role in related_roles[career_path_id]:
            if related_role in resume_analysis.detected_roles:
                relevance_score += 20
                explanations.append(f"Related role experience ({related_role.replace('_', ' ').title()})")
                break
    
    # Skill match contribution
    relevance_score += skill_match_percentage * 0.3  # 30% weight for skills
    
    # Industry relevance
    tech_paths = ['swe_backend', 'swe_frontend', 'swe_fullstack', 'devops_engineer', 'data_analyst']
    if career_path_id in tech_paths and 'tech' in resume_analysis.industry_indicators:
        relevance_score += 10
        explanations.append("Tech industry background")
    
    # Experience level appropriateness  
    if resume_analysis.experience_level in ['senior', 'mid']:
        relevance_score += 5
        explanations.append(f"Appropriate for {resume_analysis.experience_level} level")
    
    # Normalize to 0-100 scale
    relevance_score = min(100, relevance_score)
    
    explanation = "; ".join(explanations) if explanations else "Based on general skill analysis"
    
    return relevance_score, explanation

# --- API Endpoints ---

@router.get("/skills", response_model=List[Skill], tags=["Skills & Career Paths"])
async def get_all_skills():
    """
    Retrieve a list of all available skills, including learning resources.
    """
    return SKILLS_DB

@router.get("/skills/{skill_id}/learning-resources", response_model=List[LearningResource], tags=["Skills & Career Paths"])
async def get_learning_resources_for_skill(skill_id: str):
    """
    Retrieve learning resources for a specific skill.
    """
    for skill in SKILLS_DB:
        if skill.id == skill_id:
            if skill.learning_resources:
                return skill.learning_resources
            else:
                return [] # Return empty list if no resources are defined
    raise HTTPException(status_code=404, detail=f"Skill with id '{skill_id}' not found")

@router.get("/career-paths", response_model=List[CareerPath], tags=["Skills & Career Paths"])
async def get_all_career_paths():
    """
    Retrieve a list of all available career paths.
    """
    return CAREER_PATHS_DB

@router.get("/career-paths/{path_id}", response_model=CareerPath, tags=["Skills & Career Paths"])
async def get_career_path_by_id(path_id: str):
    """
    Retrieve a specific career path by its ID.
    """
    for path in CAREER_PATHS_DB:
        if path.id == path_id:
            return path
    raise HTTPException(status_code=404, detail=f"Career path with id '{path_id}' not found")

@router.post("/recommend-career-paths", tags=["Skills & Career Paths"])
async def recommend_career_paths(current_skill_ids: List[str]):
    """
    Recommend career paths based on user's current skills with match percentages.
    """
    try:
        recommendations = []
        
        for career_path in CAREER_PATHS_DB:
            path_recommendation = {
                "career_path": career_path,
                "stages_match": []
            }
            
            for stage in career_path.stages:
                required_skills = set(stage.skills_required)
                user_skills = set(current_skill_ids)
                matching_skills = required_skills.intersection(user_skills)
                
                match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
                
                stage_info = {
                    "stage_name": stage.name,
                    "match_percentage": round(match_percentage, 1),
                    "matching_skills": list(matching_skills),
                    "missing_skills": list(required_skills - user_skills),
                    "total_required": len(required_skills)
                }
                path_recommendation["stages_match"].append(stage_info)
            
            # Calculate overall path match (average of all stages)
            avg_match = sum(s["match_percentage"] for s in path_recommendation["stages_match"]) / len(path_recommendation["stages_match"])
            path_recommendation["overall_match_percentage"] = round(avg_match, 1)
            
            recommendations.append(path_recommendation)
        
        # Sort by overall match percentage
        recommendations.sort(key=lambda x: x["overall_match_percentage"], reverse=True)
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.post("/skills-gap-analysis", response_model=SkillsGapResponse, tags=["Skills & Career Paths"])
async def skills_gap_analysis(request: SkillsGapRequest):
    """
    Performs a skills gap analysis based on current skills and a target career stage.
    Identifies missing skills and suggests learning resources for them.
    """
    target_path = None
    for path in CAREER_PATHS_DB:
        if path.id == request.target_career_path_id:
            target_path = path
            break
    if not target_path:
        raise HTTPException(status_code=404, detail=f"Career path with id '{request.target_career_path_id}' not found")

    target_stage = None
    for stage in target_path.stages:
        if stage.name == request.target_stage_name:
            target_stage = stage
            break
    if not target_stage:
        raise HTTPException(status_code=404, detail=f"Stage '{request.target_stage_name}' not found in career path '{request.target_career_path_id}'")

    current_skills_details: List[Skill] = []
    for skill_id in request.current_skill_ids:
        skill_detail = get_skill_by_id(skill_id)
        if skill_detail:
            current_skills_details.append(skill_detail)
        # Silently ignore if a current_skill_id doesn't match anything in SKILLS_DB, or handle as an error?
        # For now, just include those that are found.

    required_skill_ids_for_stage = target_stage.skills_required
    required_skills_details: List[Skill] = []
    for skill_id in required_skill_ids_for_stage:
        skill_detail = get_skill_by_id(skill_id)
        if skill_detail: # Should always be found if data is consistent
            required_skills_details.append(skill_detail)
        else:
            # This would indicate an inconsistency in data, e.g. a skill_id in a career path stage that doesn't exist in SKILLS_DB
            # Consider logging a warning or raising an internal server error
            pass 

    missing_skill_ids = set(required_skill_ids_for_stage) - set(request.current_skill_ids)
    
    missing_skills_details: List[MissingSkill] = []
    for skill_id in missing_skill_ids:
        skill_detail = get_skill_by_id(skill_id)
        if skill_detail: # Should always be found
            missing_skills_details.append(MissingSkill(**skill_detail.model_dump()))

    return SkillsGapResponse(
        target_career_path_id=request.target_career_path_id,
        target_stage_name=request.target_stage_name,
        current_skills=current_skills_details,
        required_skills_for_stage=required_skills_details,
        missing_skills=missing_skills_details,
        all_skills_met=not bool(missing_skills_details)
    ) 

@router.post("/extract-skill-ids-from-text", response_model=ExtractSkillsResponse, tags=["Skills & Career Paths"])
async def extract_skill_ids_from_text(request: ExtractSkillsRequest):
    """
    Extracts known skill IDs and original skill names from a given resume text.
    Matches found skill names against the SKILLS_DB to return their IDs.
    """
    if not request.resume_text or not request.resume_text.strip():
        return ExtractSkillsResponse(success=False, skill_ids=[], extracted_skill_names=[], message="Resume text is empty.")

    # Simple lowercase text matching for this example.
    # In a real app, this would use more sophisticated NLP/parsing like in StructuredAnalyzer.
    resume_content_lower = request.resume_text.lower()
    found_skill_ids = set()
    found_skill_names = set()

    for skill_in_db in SKILLS_DB:
        # Check for skill name (e.g., "Python") and skill id (e.g., "python")
        # This is a basic check; more robust matching would be needed for variations.
        if skill_in_db.name.lower() in resume_content_lower or skill_in_db.id.lower() in resume_content_lower:
            # Try to find occurrences of the skill name or ID in the resume text
            # This is to give preference to the actual terms found if possible
            # For simplicity, just checking if the name is in the text is often enough
            
            # A more robust check would be to use a regex for whole word matching for skill_in_db.name
            # For example: re.search(r'\b' + re.escape(skill_in_db.name.lower()) + r'\b', resume_content_lower)
            if skill_in_db.name.lower() in resume_content_lower:
                 found_skill_names.add(skill_in_db.name) # Add the original cased name
                 found_skill_ids.add(skill_in_db.id)
            elif skill_in_db.id.lower() in resume_content_lower: # If only ID was found (e.g. resume says 'aws' not 'Amazon Web Services')
                 found_skill_names.add(skill_in_db.name) # Still report the proper name
                 found_skill_ids.add(skill_in_db.id)

    if not found_skill_ids:
        return ExtractSkillsResponse(success=True, skill_ids=[], extracted_skill_names=[], message="No known skills found in the resume text.")

    return ExtractSkillsResponse(
        success=True, 
        skill_ids=list(found_skill_ids),
        extracted_skill_names=list(found_skill_names),
        message=f"Successfully extracted {len(found_skill_ids)} skill(s)."
    ) 

@router.post("/intelligent-recommendation", response_model=List[IntelligentRecommendation], tags=["Skills & Career Paths"])
async def intelligent_recommendation(request: IntelligentRecommendationRequest):
    """
    Analyzes the full resume context (job titles, experience, industry) to provide smarter, more relevant career recommendations.
    Only returns the most relevant career paths based on resume analysis.
    """
    try:
        # Analyze resume context
        resume_analysis = analyze_resume_context(request.resume_text)
        
        # Get skill-based recommendations
        skill_recommendations = []
        for career_path in CAREER_PATHS_DB:
            path_recommendation = {
                "career_path": career_path,
                "stages_match": []
            }
            
            for stage in career_path.stages:
                required_skills = set(stage.skills_required)
                user_skills = set(request.current_skill_ids)
                matching_skills = required_skills.intersection(user_skills)
                
                match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
                
                stage_info = {
                    "stage_name": stage.name,
                    "match_percentage": round(match_percentage, 1),
                    "matching_skills": list(matching_skills),
                    "missing_skills": list(required_skills - user_skills),
                    "total_required": len(required_skills)
                }
                path_recommendation["stages_match"].append(stage_info)
            
            # Calculate overall path match (average of all stages)
            avg_match = sum(s["match_percentage"] for s in path_recommendation["stages_match"]) / len(path_recommendation["stages_match"])
            path_recommendation["overall_match_percentage"] = round(avg_match, 1)
            
            # Calculate relevance score based on resume analysis
            relevance_score, why_recommended = calculate_relevance_score(
                career_path.id, 
                resume_analysis, 
                avg_match
            )
            
            # Determine confidence level
            if relevance_score >= 80:
                confidence_level = "Very High"
            elif relevance_score >= 60:
                confidence_level = "High"  
            elif relevance_score >= 40:
                confidence_level = "Medium"
            elif relevance_score >= 20:
                confidence_level = "Low"
            else:
                confidence_level = "Very Low"
            
            intelligent_rec = IntelligentRecommendation(
                career_path=career_path,
                stages_match=path_recommendation["stages_match"],
                overall_match_percentage=path_recommendation["overall_match_percentage"],
                relevance_score=relevance_score,
                confidence_level=confidence_level,
                why_recommended=why_recommended,
                resume_analysis=resume_analysis
            )
            
            skill_recommendations.append(intelligent_rec)
        
        # Filter and sort recommendations
        # Only show paths with relevance score > 25 (meaningful relevance)
        filtered_recommendations = [rec for rec in skill_recommendations if rec.relevance_score > 25]
        
        # Sort by relevance score first, then by skill match
        filtered_recommendations.sort(
            key=lambda x: (x.relevance_score, x.overall_match_percentage), 
            reverse=True
        )
        
        # Return top 4 most relevant recommendations
        return filtered_recommendations[:4]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating intelligent recommendations: {str(e)}") 

def generate_skill_milestones(skill_ids: List[str], start_date: date, experience_level: str) -> List[SkillMilestone]:
    """Generate realistic skill milestones based on user's current level"""
    milestones = []
    
    # Adjust learning pace based on experience level
    pace_multiplier = {"junior": 1.5, "mid": 1.0, "senior": 0.8}[experience_level]
    
    current_date = start_date
    
    for i, skill_id in enumerate(skill_ids):
        skill = get_skill_by_id(skill_id)
        if not skill:
            continue
            
        # Simulate different difficulty levels for different skills
        difficulty_mapping = {
            "html_css": ("Beginner", 2),
            "javascript": ("Intermediate", 4), 
            "react": ("Intermediate", 6),
            "python": ("Intermediate", 4),
            "machine_learning": ("Advanced", 8),
            "kubernetes": ("Advanced", 10),
            "data_analysis": ("Intermediate", 4),
            "ui_ux_design": ("Intermediate", 5)
        }
        
        difficulty, base_weeks = difficulty_mapping.get(skill_id, ("Intermediate", 4))
        estimated_weeks = int(base_weeks * pace_multiplier)
        
        # Add some randomization to make it realistic
        estimated_weeks += random.randint(-1, 2)
        estimated_weeks = max(1, estimated_weeks)  # Minimum 1 week
        
        target_date = current_date + timedelta(weeks=estimated_weeks)
        
        milestone = SkillMilestone(
            skill_id=skill_id,
            skill_name=skill.name,
            proficiency_level=3,  # Target intermediate level
            target_date=target_date,
            estimated_learning_time_weeks=estimated_weeks,
            difficulty_level=difficulty
        )
        
        milestones.append(milestone)
        current_date = target_date + timedelta(days=7)  # 1 week buffer between skills
    
    return milestones

def generate_stage_evolutions(career_path: CareerPath, current_skills: List[str], start_date: date, experience_level: str) -> List[CareerStageEvolution]:
    """Generate stage evolution timeline for a career path"""
    evolutions = []
    current_date = start_date
    
    # Determine current stage based on skills
    current_stage_index = 0
    for i, stage in enumerate(career_path.stages):
        required_skills = set(stage.skills_required)
        current_skills_set = set(current_skills)
        match_percentage = len(required_skills.intersection(current_skills_set)) / len(required_skills) * 100
        
        if match_percentage >= 70:  # If 70%+ match, consider this the current stage
            current_stage_index = i
    
    # Generate evolutions for remaining stages
    for i, stage in enumerate(career_path.stages[current_stage_index:], current_stage_index):
        required_skills = set(stage.skills_required)
        current_skills_set = set(current_skills)
        missing_skills = list(required_skills - current_skills_set)
        
        # Calculate completion percentage
        completion_percentage = len(required_skills.intersection(current_skills_set)) / len(required_skills) * 100
        
        # Generate skill milestones for missing skills
        skill_milestones = generate_skill_milestones(missing_skills, current_date, experience_level)
        
        # Calculate stage duration based on skill learning time
        stage_duration_weeks = sum(m.estimated_learning_time_weeks for m in skill_milestones)
        stage_duration_months = max(3, int(stage_duration_weeks / 4))  # Minimum 3 months per stage
        
        target_completion = current_date + timedelta(days=stage_duration_months * 30)
        
        status = "Completed" if completion_percentage >= 100 else ("In Progress" if completion_percentage > 0 else "Not Started")
        
        evolution = CareerStageEvolution(
            stage_name=stage.name,
            start_date=current_date if i == current_stage_index else None,
            target_completion_date=target_completion,
            estimated_duration_months=stage_duration_months,
            skill_milestones=skill_milestones,
            completion_percentage=completion_percentage,
            status=status
        )
        
        evolutions.append(evolution)
        current_date = target_completion + timedelta(days=30)  # 1 month buffer between stages
    
    return evolutions

@router.post("/generate-career-trajectory", response_model=CareerTrajectory, tags=["Career Trajectory"])
async def generate_career_trajectory(request: GenerateTrajectoryRequest):
    """
    Generate a personalized career trajectory with timeline and milestones
    """
    # Find the target career path
    target_path = None
    for path in CAREER_PATHS_DB:
        if path.id == request.target_career_path_id:
            target_path = path
            break
    
    if not target_path:
        raise HTTPException(status_code=404, detail="Career path not found")
    
    # Determine target stage
    target_stage = request.target_stage_name or target_path.stages[-1].name
    
    # Set start date
    start_date = request.start_date or date.today()
    
    # Generate stage evolutions
    stage_evolutions = generate_stage_evolutions(
        target_path, 
        request.current_skill_ids, 
        start_date, 
        request.user_experience_level
    )
    
    # Calculate overall trajectory completion date
    if stage_evolutions:
        target_completion_date = max(se.target_completion_date for se in stage_evolutions if se.target_completion_date)
    else:
        target_completion_date = start_date + timedelta(days=365)  # Default 1 year
    
    # Collect all skill milestones
    all_skill_milestones = []
    for evolution in stage_evolutions:
        all_skill_milestones.extend(evolution.skill_milestones)
    
    # Find current stage
    current_stage = "Entry Level"
    for evolution in stage_evolutions:
        if evolution.status in ["In Progress", "Completed"]:
            current_stage = evolution.stage_name
    
    trajectory = CareerTrajectory(
        id=f"trajectory_{random.randint(1000, 9999)}",
        current_stage=current_stage,
        target_career_path_id=request.target_career_path_id,
        target_stage=target_stage,
        start_date=start_date,
        target_completion_date=target_completion_date,
        stage_evolutions=stage_evolutions,
        current_skills=request.current_skill_ids,
        skill_milestones=all_skill_milestones
    )
    
    return trajectory

@router.post("/skill-evolution", response_model=List[SkillEvolution], tags=["Career Trajectory"])
async def generate_skill_evolution(request: SkillEvolutionRequest):
    """
    Generate skill evolution tracking with historical and projected data
    """
    evolutions = []
    
    for skill_id in request.skill_ids:
        skill = get_skill_by_id(skill_id)
        if not skill:
            continue
        
        # Generate historical data (simulate past 12 months)
        historical_levels = []
        base_level = random.randint(1, 3)  # Starting level
        current_level = base_level
        
        for i in range(12, 0, -1):
            # Simulate gradual improvement
            if random.random() < 0.3:  # 30% chance of improvement each month
                current_level = min(5, current_level + 0.5)
            
            month_date = (date.today() - timedelta(days=30*i)).strftime("%Y-%m")
            historical_levels.append({
                "date": month_date,
                "level": round(current_level, 1)
            })
        
        # Generate projected data
        projected_levels = []
        learning_velocity = random.uniform(0.8, 1.5)  # Skills improvement per month
        
        for i in range(1, request.timeline_months + 1):
            # Project future improvement based on learning velocity
            current_level = min(5, current_level + (learning_velocity * 0.2))
            
            future_date = (date.today() + timedelta(days=30*i)).strftime("%Y-%m")
            projected_levels.append({
                "date": future_date,
                "level": round(current_level, 1)
            })
        
        # Predict mastery date (when skill reaches level 4.5+)
        mastery_date = None
        for proj in projected_levels:
            if proj["level"] >= 4.5:
                mastery_date = datetime.strptime(proj["date"], "%Y-%m").date()
                break
        
        evolution = SkillEvolution(
            skill_id=skill_id,
            skill_name=skill.name,
            historical_levels=historical_levels,
            projected_levels=projected_levels,
            learning_velocity=learning_velocity,
            mastery_prediction_date=mastery_date
        )
        
        evolutions.append(evolution)
    
    return evolutions

@router.post("/industry-transition-analysis", response_model=List[IndustryTransition], tags=["Career Trajectory"])
async def analyze_industry_transition(request: IndustryTransitionRequest):
    """
    Analyze potential industry transition pathways
    """
    # Find relevant transitions
    relevant_transitions = []
    
    for transition in INDUSTRY_TRANSITIONS_DB:
        if (transition.from_industry.lower() == request.current_industry.lower() and 
            transition.to_industry.lower() == request.target_industry.lower()):
            
            # Calculate how many required skills the user already has
            required_skills_set = set(transition.required_skills)
            current_skills_set = set(request.current_skills)
            skills_overlap = len(required_skills_set.intersection(current_skills_set))
            
            # Adjust difficulty and timeline based on current skills
            if skills_overlap >= len(required_skills_set) * 0.8:  # Have 80%+ skills
                transition.transition_difficulty = "Easy"
                transition.estimated_transition_time_months = max(2, int(transition.estimated_transition_time_months * 0.5))
            elif skills_overlap >= len(required_skills_set) * 0.5:  # Have 50%+ skills
                transition.transition_difficulty = "Medium"
                transition.estimated_transition_time_months = max(3, int(transition.estimated_transition_time_months * 0.75))
            
            relevant_transitions.append(transition)
    
    # If no direct transitions found, suggest general tech transition paths
    if not relevant_transitions:
        generic_transition = IndustryTransition(
            from_industry=request.current_industry,
            to_industry=request.target_industry,
            required_skills=["communication", "problem_solving", "data_analysis", "project_management"],
            transition_difficulty="Medium",
            estimated_transition_time_months=8,
            common_transition_roles=["Business Analyst", "Project Manager", "Operations Specialist"],
            success_rate=0.70
        )
        relevant_transitions.append(generic_transition)
    
    return relevant_transitions

@router.get("/career-growth-patterns", response_model=List[CareerGrowthPattern], tags=["Career Trajectory"])
async def get_career_growth_patterns():
    """
    Get available career growth patterns showing typical progression paths
    """
    return CAREER_GROWTH_PATTERNS_DB

@router.get("/career-growth-patterns/{pattern_id}", response_model=CareerGrowthPattern, tags=["Career Trajectory"])
async def get_career_growth_pattern(pattern_id: str):
    """
    Get a specific career growth pattern by ID
    """
    for pattern in CAREER_GROWTH_PATTERNS_DB:
        if pattern.pattern_id == pattern_id:
            return pattern
    
    raise HTTPException(status_code=404, detail="Career growth pattern not found") 