"""
Resume parsing services to extract key information.
"""
from typing import List, Dict, Any
import re

def extract_skills(resume_text: str) -> List[str]:
    """
    Extract skills from a resume text.
    
    Args:
        resume_text: The text content of the resume
        
    Returns:
        List of extracted skills
    """
    # In a real implementation, this would use more sophisticated NLP techniques
    # For this example, we'll use a simplified approach
    
    # Create a simple pattern to match common skill sections
    skill_section_pattern = re.compile(
        r"(?:technical skills|skills|technologies|tools|languages|frameworks|proficiencies)[\s\n:]+(.+?)(?:\n\n|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    
    skill_matches = skill_section_pattern.findall(resume_text)
    
    if skill_matches:
        # Extract skills from the matched sections
        skills_text = " ".join(skill_matches)
        
        # Split by common separators like commas, bullets, etc.
        skills = re.split(r'[,•|/\n]+', skills_text)
        
        # Clean up and normalize skills
        skills = [skill.strip() for skill in skills if skill.strip()]
        
        return skills
    
    # Fallback method: look for common programming languages, tools, etc.
    common_skills = [
        "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "SQL", "HTML", "CSS",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Jenkins",
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision"
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills

def extract_experience(resume_text: str) -> List[Dict[str, Any]]:
    """
    Extract work experience from a resume text.
    
    Args:
        resume_text: The text content of the resume
        
    Returns:
        List of dictionaries containing job details
    """
    # In a real implementation, this would use more sophisticated NLP techniques
    # For this example, we'll use a simplified approach
    
    # Find the experience section
    experience_section_pattern = re.compile(
        r"(?:work experience|experience|employment|professional experience)[\s\n:]+(.+?)(?:\n\n|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    
    experience_matches = experience_section_pattern.findall(resume_text)
    
    if not experience_matches:
        return []
    
    experiences_text = experience_matches[0]
    
    # Look for job entries
    job_pattern = re.compile(
        r"(?P<company>[\w\s&.,]+?),?\s+(?P<title>[\w\s&.,]+?),?\s+(?P<dates>\d{1,2}/\d{4}\s*[-–]\s*(?:\d{1,2}/\d{4}|Present))",
        re.IGNORECASE
    )
    
    jobs = []
    for match in job_pattern.finditer(experiences_text):
        company = match.group("company").strip()
        title = match.group("title").strip()
        dates = match.group("dates").strip()
        
        # Get the description following this match until the next job or the end
        start_pos = match.end()
        next_match = job_pattern.search(experiences_text, start_pos)
        end_pos = next_match.start() if next_match else len(experiences_text)
        
        description = experiences_text[start_pos:end_pos].strip()
        
        jobs.append({
            "company": company,
            "title": title,
            "dates": dates,
            "description": description
        })
    
    # If regular pattern matching fails, try a simpler approach
    if not jobs:
        # Look for lines that might contain job titles or companies
        lines = experiences_text.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # If we see something that looks like a date range, this is likely a new job
            if re.search(r'\d{4}\s*[-–]\s*(?:\d{4}|Present)', line, re.IGNORECASE):
                if current_job and "title" in current_job:
                    jobs.append(current_job)
                current_job = {"dates": line}
            elif not current_job:
                current_job = {"title": line}
            elif "title" in current_job and "company" not in current_job:
                current_job["company"] = line
            elif "description" not in current_job:
                current_job["description"] = line
            else:
                current_job["description"] += " " + line
        
        if current_job and "title" in current_job:
            jobs.append(current_job)
    
    return jobs

def extract_education(resume_text: str) -> List[Dict[str, Any]]:
    """
    Extract education details from a resume text.
    
    Args:
        resume_text: The text content of the resume
        
    Returns:
        List of dictionaries containing education details
    """
    # Find the education section
    education_section_pattern = re.compile(
        r"(?:education|educational background|academic background)[\s\n:]+(.+?)(?:\n\n|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    
    education_matches = education_section_pattern.findall(resume_text)
    
    if not education_matches:
        return []
    
    education_text = education_matches[0]
    
    # Look for degree entries
    degree_pattern = re.compile(
        r"(?P<degree>(?:Bachelor|Master|PhD|Doctor|B\.S\.|M\.S\.|Ph\.D\.|B\.A\.|M\.A\.|M\.B\.A\.|B\.Tech|M\.Tech)[\w\s.,]+?),?\s+(?P<institution>[\w\s&.,]+?),?\s+(?P<dates>\d{1,2}/\d{4}\s*[-–]\s*(?:\d{1,2}/\d{4}|Present))",
        re.IGNORECASE
    )
    
    education = []
    for match in degree_pattern.finditer(education_text):
        degree = match.group("degree").strip()
        institution = match.group("institution").strip()
        dates = match.group("dates").strip()
        
        education.append({
            "degree": degree,
            "institution": institution,
            "dates": dates
        })
    
    # If regular pattern matching fails, try a simpler approach
    if not education:
        # Look for common degree keywords
        degree_keywords = [
            "Bachelor", "Master", "PhD", "Doctor", "B.S.", "M.S.", "Ph.D.",
            "B.A.", "M.A.", "M.B.A.", "B.Tech", "M.Tech"
        ]
        
        lines = education_text.split('\n')
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line contains a degree keyword
            has_degree = any(keyword in line for keyword in degree_keywords)
            
            if has_degree:
                if current_edu and "degree" in current_edu:
                    education.append(current_edu)
                current_edu = {"degree": line}
            elif not current_edu:
                # This might be an institution without explicit degree mention
                current_edu = {"institution": line}
            elif "degree" in current_edu and "institution" not in current_edu:
                current_edu["institution"] = line
            elif "dates" not in current_edu and re.search(r'\d{4}', line):
                current_edu["dates"] = line
        
        if current_edu and "degree" in current_edu:
            education.append(current_edu)
    
    return education