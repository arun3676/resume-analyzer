"""
Resume analysis services.
"""
from typing import List, Dict, Any, Tuple

def analyze_strengths_weaknesses(
    skills: List[str], 
    experience: List[Dict[str, Any]], 
    education: List[Dict[str, Any]]
) -> Dict[str, List[str]]:
    """
    Analyze the strengths and weaknesses based on the resume components.
    
    Args:
        skills: List of extracted skills
        experience: List of extracted work experiences
        education: List of extracted education details
        
    Returns:
        Dictionary with strengths and weaknesses lists
    """
    strengths = []
    weaknesses = []
    
    # Analyze skills
    if len(skills) >= 10:
        strengths.append("Diverse skill set with multiple technical competencies")
    else:
        weaknesses.append("Limited range of technical skills listed")
    
    # Check for in-demand skills
    in_demand_skills = [
        "Python", "Machine Learning", "Deep Learning", "AWS", "Azure", 
        "Docker", "Kubernetes", "React", "JavaScript", "SQL", "NoSQL",
        "TensorFlow", "PyTorch", "Data Science", "NLP", "Cloud"
    ]
    
    matching_in_demand = set(skills).intersection(set(in_demand_skills))
    if matching_in_demand:
        strengths.append(f"Possesses in-demand skills: {', '.join(matching_in_demand)}")
    else:
        weaknesses.append("Few in-demand tech skills explicitly listed")
    
    # Analyze experience
    if len(experience) >= 3:
        strengths.append("Solid work history with multiple positions")
    elif len(experience) == 0:
        weaknesses.append("No work experience listed")
    else:
        weaknesses.append("Limited work history")
    
    # Look for experience descriptions
    has_detailed_descriptions = any(len(job.get("description", "")) > 100 for job in experience)
    if has_detailed_descriptions:
        strengths.append("Detailed job descriptions with specific accomplishments")
    else:
        weaknesses.append("Job descriptions lack detail or quantifiable achievements")
    
    # Analyze education
    has_advanced_degree = any("master" in edu.get("degree", "").lower() or 
                             "phd" in edu.get("degree", "").lower() or
                             "doctor" in edu.get("degree", "").lower()
                             for edu in education)
    
    if has_advanced_degree:
        strengths.append("Advanced degree demonstrates specialized knowledge")
    elif not education:
        weaknesses.append("No formal education listed")
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses
    }

def calculate_job_match(
    skills: List[str], 
    experience: List[Dict[str, Any]], 
    education: List[Dict[str, Any]], 
    job_description: str
) -> Dict[str, Any]:
    """
    Calculate how well the resume matches a job description.
    
    Args:
        skills: List of extracted skills
        experience: List of extracted work experiences
        education: List of extracted education details
        job_description: The job description text
        
    Returns:
        Dictionary with match percentage and details
    """
    # In a real implementation, this would use more sophisticated NLP techniques
    # such as semantic similarity. For this example, we'll use a simplified approach.
    
    # Extract skills from job description (simplified approach)
    job_skills = []
    common_skills = [
        "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "SQL", "HTML", "CSS",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Jenkins",
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision"
    ]
    
    for skill in common_skills:
        if skill.lower() in job_description.lower():
            job_skills.append(skill)
    
    # Calculate skill match
    matching_skills = set(s.lower() for s in skills).intersection(set(s.lower() for s in job_skills))
    skill_match_percent = len(matching_skills) / len(job_skills) * 100 if job_skills else 0
    
    # Look for experience requirements
    years_required = 0
    experience_words = ["years", "year", "yr", "yrs"]
    import re
    experience_pattern = re.compile(r'(\d+)[\+]?\s*(?:' + '|'.join(experience_words) + ')', re.IGNORECASE)
    matches = experience_pattern.findall(job_description)
    if matches:
        years_required = int(matches[0])
    
    # Estimate years of experience from resume
    years_experience = sum(1 for _ in experience)  # Simplified, assumes 1 year per job
    experience_match_percent = min(years_experience / years_required * 100, 100) if years_required > 0 else 100
    
    # Check for education requirements
    education_required = ""
    if "bachelor" in job_description.lower() or "bs" in job_description.lower() or "ba" in job_description.lower():
        education_required = "Bachelor's"
    if "master" in job_description.lower() or "ms" in job_description.lower() or "ma" in job_description.lower():
        education_required = "Master's"
    if "phd" in job_description.lower() or "doctor" in job_description.lower():
        education_required = "PhD"
    
    # Check if the candidate meets education requirements
    education_match = False
    if education_required:
        for edu in education:
            degree = edu.get("degree", "").lower()
            if education_required == "Bachelor's" and ("bachelor" in degree or "bs" in degree or "ba" in degree):
                education_match = True
            elif education_required == "Master's" and ("master" in degree or "ms" in degree or "ma" in degree):
                education_match = True
            elif education_required == "PhD" and ("phd" in degree or "doctor" in degree):
                education_match = True
    else:
        education_match = True  # No specific requirement
    
    education_match_percent = 100 if education_match else 0
    
    # Calculate overall match
    overall_match = (skill_match_percent + experience_match_percent + education_match_percent) / 3
    
    return {
        "overall_match_percent": round(overall_match, 1),
        "skill_match_percent": round(skill_match_percent, 1),
        "experience_match_percent": round(experience_match_percent, 1),
        "education_match_percent": round(education_match_percent, 1),
        "matching_skills": list(matching_skills),
        "missing_skills": list(set(s.lower() for s in job_skills) - set(s.lower() for s in skills))
    }

def suggest_improvements(
    resume_text: str, 
    strengths: List[str], 
    weaknesses: List[str]
) -> List[str]:
    """
    Suggest improvements for the resume based on identified strengths and weaknesses.
    
    Args:
        resume_text: The text content of the resume
        strengths: List of identified strengths
        weaknesses: List of identified weaknesses
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    # Address weaknesses
    for weakness in weaknesses:
        if "limited range" in weakness.lower():
            suggestions.append("Expand the skills section to include more relevant technologies and tools")
        
        if "few in-demand" in weakness.lower():
            suggestions.append("Add more in-demand skills like Python, AWS, or Machine Learning if applicable")
        
        if "no work experience" in weakness.lower() or "limited work history" in weakness.lower():
            suggestions.append("Include relevant projects, internships, or volunteer work to demonstrate practical experience")
        
        if "job descriptions lack detail" in weakness.lower():
            suggestions.append("Enhance job descriptions with specific achievements, metrics, and outcomes")
        
        if "no formal education" in weakness.lower():
            suggestions.append("Include any relevant education, certifications, or courses")
    
    # General improvements
    if "summary" not in resume_text.lower() or "objective" not in resume_text.lower():
        suggestions.append("Add a compelling professional summary or objective statement at the beginning")
    
    if not any(word in resume_text.lower() for word in ["achieved", "improved", "increased", "reduced", "managed", "led"]):
        suggestions.append("Use strong action verbs and quantify achievements where possible (e.g., 'Increased efficiency by 20%')")
    
    if "linkedin" not in resume_text.lower():
        suggestions.append("Include your LinkedIn profile URL for additional professional information")
    
    return suggestions