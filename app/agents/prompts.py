"""
Prompts for the Resume Analyzer ReAct agent.
"""

REACT_SYSTEM_PROMPT = """You are a professional Resume Analyzer that analyzes resumes to extract information, provide insights, and match candidates to job descriptions."""

RESUME_ANALYSIS_PROMPT = """
Analyze the following resume:

Resume:
{resume_text}

{job_description}

Provide:
1. Key skills & experience
2. Strengths & weaknesses
3. Improvement suggestions
4. Job match assessment (if job description provided). Include a list of matched skills, skills found in the resume, skills found in the job description, and a skill match percentage.
"""