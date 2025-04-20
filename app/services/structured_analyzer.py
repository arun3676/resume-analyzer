"""
Advanced resume analyzer with structured output.
"""
from typing import Dict, List, Any, Optional
import re
from app.services.parser import extract_skills, extract_experience, extract_education
from app.services.skills_kb import match_skills, get_related_skills

class StructuredAnalyzer:
    """
    Analyzes resumes and produces structured output without heavy API usage.
    """
    
    def __init__(self):
        """Initialize the structured analyzer."""
        pass
    
    def extract_job_skills(self, job_description: str) -> List[str]:
        """
        Extract required skills from a job description.
        """
        if not job_description:
            return []
            
        # Look for skills sections in job description
        skills_section_patterns = [
            r"(?:skills|requirements|qualifications|what you('ll| will) need)[:\s]+(.+?)(?:\n\n|\Z)",
            r"technical skills[:\s]+(.+?)(?:\n\n|\Z)",
            r"you have[:\s]+(.+?)(?:\n\n|\Z)",
        ]
        
        skills = []
        for pattern in skills_section_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE | re.DOTALL)
            if matches:
                skills_text = matches[0] if isinstance(matches[0], str) else matches[0][1]
                
                # Extract skills from bullet points or commas
                skill_items = re.findall(r'[•\-*]\s*([^•\-*\n]+)', skills_text)
                if skill_items:
                    skills.extend([s.strip() for s in skill_items])
                else:
                    # Split by commas if no bullet points
                    skills.extend([s.strip() for s in skills_text.split(',')])
        
        # Look for specific skill keywords throughout the text
        common_skill_patterns = [
            r"experience (?:with|in) ([^,.]+)",
            r"knowledge of ([^,.]+)",
            r"familiarity with ([^,.]+)",
            r"proficiency in ([^,.]+)",
            r"proficient (?:with|in) ([^,.]+)",
            r"understanding of ([^,.]+)",
        ]
        
        for pattern in common_skill_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            skills.extend([s.strip() for s in matches])
        
        # Clean up skills
        cleaned_skills = []
        for skill in skills:
            # Remove common endings
            skill = re.sub(r'(?:is required|required|a must|a plus|preferred)$', '', skill, flags=re.IGNORECASE)
            skill = skill.strip()
            if skill and len(skill) > 2 and skill not in cleaned_skills:
                cleaned_skills.append(skill)
        
        return cleaned_skills
    
    def analyze_resume(self, resume_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a resume and optionally match it against a job description.
        
        Args:
            resume_text: The text content of the resume
            job_description: Optional job description to match against
            
        Returns:
            Dictionary with structured analysis results
        """
        # Extract basic components from the resume
        resume_skills = extract_skills(resume_text)
        resume_experience = extract_experience(resume_text)
        resume_education = extract_education(resume_text)
        
        # Analyze experience level
        years_experience = sum(1 for _ in resume_experience)  # Simplified, assumes 1 year per job
        
        # Identify education level
        education_level = "Unknown"
        for edu in resume_education:
            degree = edu.get("degree", "").lower()
            if "phd" in degree or "doctor" in degree:
                education_level = "PhD"
                break
            elif "master" in degree or "ms" in degree or "ma" in degree:
                education_level = "Master's"
                break
            elif "bachelor" in degree or "bs" in degree or "ba" in degree:
                education_level = "Bachelor's"
                break
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        # Skills-based strengths/weaknesses
        if len(resume_skills) >= 10:
            strengths.append("Diverse skill set with multiple technical competencies")
        else:
            weaknesses.append("Limited range of technical skills listed")
        
        # Experience-based strengths/weaknesses
        if years_experience >= 3:
            strengths.append(f"{years_experience}+ years of relevant work experience")
        elif years_experience == 0:
            weaknesses.append("No work experience listed")
        else:
            weaknesses.append("Limited work history")
        
        # Education-based strengths/weaknesses
        if education_level in ["Master's", "PhD"]:
            strengths.append(f"Advanced degree ({education_level})")
        elif education_level == "Unknown":
            weaknesses.append("Education details unclear or not specified")
        
        # Job matching if job description is provided
        job_match = None
        if job_description:
            job_skills = self.extract_job_skills(job_description)
            job_match = match_skills(resume_skills, job_skills)
            
            # Add match-based strengths/weaknesses
            match_percent = job_match.get("match_percentage", 0)
            if match_percent >= 80:
                strengths.append(f"Strong match ({match_percent}%) with job requirements")
            elif match_percent <= 50:
                weaknesses.append(f"Low match ({match_percent}%) with job requirements")
                
                # Suggest improvement for missing skills
                missing = job_match.get("missing_skills", [])
                if missing:
                    top_missing = missing[:3]
                    weaknesses.append(f"Missing key skills: {', '.join(top_missing)}")
        
        # Generate improvement suggestions
        suggestions = []
        
        if "Limited range of technical skills listed" in weaknesses:
            suggestions.append("Expand your skills section to include more relevant technologies")
        
        if "Limited work history" in weaknesses:
            suggestions.append("Add more details about your work experience, including measurable achievements")
        
        if job_match and job_match.get("match_percentage", 0) < 70:
            suggestions.append("Tailor your resume to highlight skills relevant to this specific job")
        
        if "summary" not in resume_text.lower():
            suggestions.append("Add a professional summary at the beginning of your resume")
        
        # Combine all analysis into a structured result
        result = {
            "basic_info": {
                "skills": resume_skills,
                "experience_years": years_experience,
                "education_level": education_level,
            },
            "analysis": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions,
            }
        }
        
        if job_match:
            result["job_match"] = job_match
        
        # Generate a human-readable summary
        summary = self._generate_summary(result, job_description is not None)
        result["summary"] = summary
        
        return result
    
    def _generate_summary(self, result: Dict[str, Any], has_job_description: bool) -> str:
        """
        Generate a human-readable summary from the structured analysis.
        """
        basic_info = result.get("basic_info", {})
        analysis = result.get("analysis", {})
        job_match = result.get("job_match", {})
        
        summary = "# Resume Analysis Summary\n\n"
        
        # Add basic info
        summary += "## Candidate Profile\n\n"
        summary += f"* **Skills**: {', '.join(basic_info.get('skills', [])[:8])}\n"
        summary += f"* **Experience**: {basic_info.get('experience_years', 0)} years\n"
        summary += f"* **Education**: {basic_info.get('education_level', 'Not specified')}\n\n"
        
        # Add strengths and weaknesses
        summary += "## Strengths\n\n"
        for strength in analysis.get("strengths", []):
            summary += f"* {strength}\n"
        summary += "\n"
        
        summary += "## Areas for Improvement\n\n"
        for weakness in analysis.get("weaknesses", []):
            summary += f"* {weakness}\n"
        summary += "\n"
        
        # Add job match if available
        if has_job_description and job_match:
            match_percent = job_match.get("match_percentage", 0)
            summary += f"## Job Match: {match_percent}%\n\n"
            
            # Direct matches
            direct_matches = job_match.get("direct_matches", [])
            if direct_matches:
                summary += "### Direct Skill Matches\n\n"
                for skill in direct_matches[:5]:
                    summary += f"* {skill}\n"
                summary += "\n"
            
            # Related matches
            related_matches = job_match.get("related_matches", [])
            if related_matches:
                summary += "### Related Skill Matches\n\n"
                for match in related_matches[:3]:
                    job_skill = match.get("job_skill", "")
                    matched_via = match.get("matched_via", [])
                    summary += f"* {job_skill} (via {', '.join(matched_via[:2])})\n"
                summary += "\n"
            
            # Missing skills
            missing_skills = job_match.get("missing_skills", [])
            if missing_skills:
                summary += "### Missing Skills\n\n"
                for skill in missing_skills[:5]:
                    summary += f"* {skill}\n"
                summary += "\n"
        
        # Add suggestions
        summary += "## Suggestions for Improvement\n\n"
        for suggestion in analysis.get("suggestions", []):
            summary += f"* {suggestion}\n"
        
        return summary