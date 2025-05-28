"""
AI-powered Resume Builder and Optimizer Service.
This service generates tailored resumes based on job descriptions and user information.
"""
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from app.config import OPENAI_API_KEY

class ResumeBuilder:
    """AI-powered resume builder that creates optimized resumes."""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def build_resume(
        self, 
        user_info: Dict[str, Any], 
        job_description: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build an optimized resume based on user information and job requirements.
        
        Args:
            user_info: Dictionary containing user's skills, experience, education, etc.
            job_description: Optional job description to tailor the resume
            target_role: Optional target role title
            
        Returns:
            Generated resume with optimized content
        """
        
        prompt = self._create_resume_building_prompt(user_info, job_description, target_role)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert resume writer and career coach with 15+ years of experience helping people land their dream jobs. You understand ATS systems, hiring manager preferences, and industry best practices."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                resume_data = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                resume_data = {
                    "success": True,
                    "resume_content": content,
                    "optimizations_applied": ["Content generated but parsing failed"],
                    "ats_score": 85
                }
            
            return resume_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "resume_content": "",
                "optimizations_applied": [],
                "ats_score": 0
            }
    
    def optimize_existing_resume(
        self, 
        current_resume: str, 
        job_description: str,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize an existing resume for a specific job.
        
        Args:
            current_resume: Current resume text
            job_description: Job description to optimize for
            focus_areas: Specific areas to focus on (e.g., ['skills', 'experience'])
            
        Returns:
            Optimized resume with improvements
        """
        
        focus_areas = focus_areas or ['skills', 'experience', 'summary', 'keywords']
        
        prompt = f"""
        RESUME OPTIMIZATION TASK:
        
        Current Resume:
        {current_resume}
        
        Target Job Description:
        {job_description}
        
        Focus Areas: {', '.join(focus_areas)}
        
        Please optimize this resume for the target job. Provide:
        
        1. OPTIMIZED RESUME (complete rewritten version)
        2. KEY IMPROVEMENTS made
        3. ATS COMPATIBILITY SCORE (0-100)
        4. KEYWORD MATCHES added
        5. SPECIFIC RECOMMENDATIONS for further improvement
        
        Return your response as JSON in this format:
        {{
            "optimized_resume": "Complete optimized resume text...",
            "improvements": ["List of key improvements made"],
            "ats_score": 90,
            "keywords_added": ["keyword1", "keyword2"],
            "recommendations": ["Further recommendations"],
            "match_percentage": 85,
            "success": true
        }}
        
        Focus on:
        - Matching job requirements with candidate experience
        - Using relevant keywords naturally
        - Quantifying achievements with metrics
        - Improving ATS readability
        - Highlighting transferable skills
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert resume optimizer specializing in ATS systems and keyword optimization. You help candidates tailor their resumes for specific jobs while maintaining authenticity."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            
            try:
                optimization_data = json.loads(content)
                return optimization_data
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "optimized_resume": content,
                    "improvements": ["Resume optimized but parsing failed"],
                    "ats_score": 80,
                    "keywords_added": [],
                    "recommendations": [],
                    "match_percentage": 75
                }
                
        except Exception as e:
            print(f"Error in optimize_existing_resume: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "optimized_resume": current_resume,
                "improvements": [],
                "ats_score": 0,
                "keywords_added": [],
                "recommendations": [],
                "match_percentage": 0
            }
    
    def generate_multiple_versions(
        self, 
        user_info: Dict[str, Any], 
        job_description: str,
        num_versions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple versions of a resume for A/B testing.
        
        Args:
            user_info: User information
            job_description: Target job description
            num_versions: Number of versions to generate
            
        Returns:
            List of different resume versions
        """
        
        versions = []
        styles = [
            "professional and conservative",
            "modern and creative", 
            "technical and detailed"
        ]
        
        for i in range(min(num_versions, len(styles))):
            style = styles[i]
            
            prompt = f"""
            CRITICAL TASK: Create a resume version with a DISTINCTLY '{style}' style.
            The style MUST be clearly reflected in the tone, structure, and content.
            DO NOT generate a generic resume. Emphasize the '{style}' characteristics.
            
            Candidate Information:
            {json.dumps(user_info, indent=2)}
            
            Job Description:
            {job_description}
            
            Requested Style (Strict Adherence Required): {style}
            
            Create a complete resume optimized for this style and job. Return as JSON:
            {{
                "style": "{style}",
                "resume_content": "Complete resume text, strongly reflecting the '{style}' style...",
                "key_features": ["Feature 1 reflecting '{style}'", "Feature 2 reflecting '{style}'"],
                "target_audience": "Description of who this '{style}' version works best for",
                "ats_score": 85,
                "success": true
            }}
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": f"You are an expert resume writer. Your current task is to generate a resume that STRICTLY ADHERES to the '{style}' style. The difference in style MUST be obvious."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=2500
                )
                
                content = response.choices[0].message.content
                
                try:
                    version_data = json.loads(content)

                    # Initial check and sanitization of resume_content
                    if isinstance(version_data.get("resume_content"), dict):
                        print(f"DEBUG: resume_content for style '{style}' was a dict, converting to JSON string.")
                        version_data["resume_content"] = json.dumps(version_data["resume_content"], indent=2)
                    elif not isinstance(version_data.get("resume_content"), str):
                        print(f"DEBUG: resume_content for style '{style}' was not a dict or str (type: {type(version_data.get('resume_content'))}), converting to str.")
                        version_data["resume_content"] = str(version_data.get("resume_content", "Content not available"))
                    else:
                        print(f"DEBUG: resume_content for style '{style}' is already a string.")

                    # Specific check for 'technical and detailed' style if it looks like raw user_info
                    if style == "technical and detailed":
                        try:
                            # Attempt to parse resume_content as JSON
                            parsed_resume_content = json.loads(version_data.get("resume_content", ""))
                            # Check if it has the structure of user_info
                            if isinstance(parsed_resume_content, dict) and all(k in parsed_resume_content for k in ["personal_info", "skills", "experience"]):
                                print(f"DEBUG: 'technical and detailed' resume_content appears to be raw user_info. Attempting re-generation.")
                                
                                regeneration_prompt = f'''
                                The previous attempt to generate a 'technical and detailed' resume resulted in raw JSON data.
                                This is INCORRECT.
                                Please generate ONLY the 'resume_content' as a proper, formatted resume TEXT,
                                based on the following candidate information and job description.
                                The resume text should be narrative and well-structured, NOT a JSON dump.
                                It MUST be highly technical and detailed, focusing on specific accomplishments, tools, and metrics.

                                Candidate Information:
                                {json.dumps(user_info, indent=2)}

                                Job Description:
                                {job_description}

                                Generate ONLY the 'resume_content' text.
                                '''
                                retry_response = self.client.chat.completions.create(
                                    model="gpt-4",
                                    messages=[
                                        {"role": "system", "content": "You are an expert resume writer. Your task is to generate ONLY the text for a resume's content section. It must be in a narrative, formatted style suitable for a resume, focusing on technical details."},
                                        {"role": "user", "content": regeneration_prompt}
                                    ],
                                    temperature=0.5, # Slightly lower temp for more focused regeneration
                                    max_tokens=2000
                                )
                                regenerated_content = retry_response.choices[0].message.content
                                version_data["resume_content"] = regenerated_content
                                print(f"DEBUG: Re-generated 'technical and detailed' resume_content.")
                        except json.JSONDecodeError:
                            # It wasn't a JSON string resembling user_info, so proceed
                            pass 
                        except Exception as regen_e:
                            print(f"DEBUG: Error during 'technical and detailed' re-generation: {str(regen_e)}")


                    print(f"DEBUG: Final resume_content for style '{style}' (type: {type(version_data.get('resume_content'))}):")
                    print(f"DEBUG CONTENT PREVIEW: {str(version_data.get('resume_content'))[:200]}...") # Print a preview
                    versions.append(version_data)
                except json.JSONDecodeError:
                    print(f"DEBUG: JSONDecodeError for style '{style}'. Using raw content for resume_content.")
                    print(f"DEBUG: Raw content for style '{style}' (type: {type(content)}):")
                    print(f"DEBUG RAW CONTENT PREVIEW: {str(content)[:200]}...") # Print a preview
                    versions.append({
                        "style": style,
                        "resume_content": content, # content is already a string here
                        "key_features": [f"{style} format"],
                        "target_audience": "General audience",
                        "ats_score": 80,
                        "success": True
                    })
                    
            except Exception as e:
                versions.append({
                    "style": style,
                    "resume_content": f"Error generating {style} version: {str(e)}",
                    "key_features": [],
                    "target_audience": "",
                    "ats_score": 0,
                    "success": False,
                    "error": str(e)
                })
        
        return versions
    
    def _create_resume_building_prompt(
        self, 
        user_info: Dict[str, Any], 
        job_description: Optional[str], 
        target_role: Optional[str]
    ) -> str:
        """Create the prompt for resume building."""
        
        prompt = f"""
        RESUME BUILDING TASK:
        
        Build a professional, ATS-optimized resume for this candidate.
        
        Candidate Information:
        {json.dumps(user_info, indent=2)}
        """
        
        if target_role:
            prompt += f"\nTarget Role: {target_role}"
        
        if job_description:
            prompt += f"""
            
            Target Job Description:
            {job_description}
            """
        
        prompt += """
        
        Create a complete, professional resume that:
        1. Highlights relevant skills and experience
        2. Uses strong action verbs and quantified achievements
        3. Is optimized for ATS systems
        4. Matches the job requirements (if provided)
        5. Has a compelling professional summary
        6. Uses industry-standard formatting
        
        Return your response as JSON in this format:
        {
            "professional_summary": "Compelling 3-4 line summary...",
            "skills": ["skill1", "skill2", "skill3"],
            "experience": [
                {
                    "title": "Job Title",
                    "company": "Company Name", 
                    "dates": "MM/YYYY - MM/YYYY",
                    "achievements": ["Achievement 1", "Achievement 2"]
                }
            ],
            "education": [
                {
                    "degree": "Degree Name",
                    "institution": "School Name",
                    "year": "YYYY"
                }
            ],
            "optimizations_applied": ["List of optimizations made"],
            "ats_score": 90,
            "match_percentage": 85,
            "success": true
        }
        
        Focus on:
        - Relevance to target role
        - Quantified achievements
        - ATS keyword optimization
        - Professional presentation
        - Clear value proposition
        """
        
        return prompt 