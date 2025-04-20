"""
Skills knowledge base for smarter skill matching without relying on API calls.
"""
import json
from pathlib import Path
import os

# Main skills categories and related skills
SKILLS_RELATIONSHIPS = {
    "Machine Learning": [
        "Deep Learning", "Neural Networks", "Supervised Learning", "Unsupervised Learning", 
        "Reinforcement Learning", "Classification", "Regression", "Clustering", 
        "Dimensionality Reduction", "Feature Engineering", "Model Selection",
        "Hyperparameter Tuning", "Cross-Validation", "Transfer Learning"
    ],
    
    "LLM Knowledge": [
        "Prompt Engineering", "Fine-tuning LLMs", "RAG", "Retrieval Augmented Generation",
        "Token Management", "Embeddings", "In-context Learning", "Chain-of-Thought",
        "Few-shot Learning", "Zero-shot Learning", "Prompt Templates", "Semantic Search",
        "Vector Databases", "LangChain", "LlamaIndex", "Transformer Architecture"
    ],
    
    "Data Science": [
        "Data Analysis", "Data Visualization", "Statistical Analysis", "Hypothesis Testing",
        "Experimental Design", "A/B Testing", "Data Cleaning", "Data Wrangling",
        "ETL", "Data Pipeline", "Business Intelligence", "Dashboarding"
    ],
    
    "Programming Languages": [
        "Python", "R", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust",
        "SQL", "Scala", "Julia", "MATLAB", "C#", "PHP", "Ruby", "Swift"
    ],
    
    "ML Frameworks": [
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "XGBoost", "LightGBM",
        "CatBoost", "Hugging Face", "Transformers", "MXNet", "ONNX", "OpenCV"
    ],
    
    "Big Data": [
        "Apache Spark", "Hadoop", "Kafka", "Storm", "Flink", "Hive", "Pig",
        "MapReduce", "Distributed Systems", "Data Lake", "Data Warehouse"
    ],
    
    "Cloud Platforms": [
        "AWS", "Azure", "GCP", "S3", "EC2", "SageMaker", "Azure ML", 
        "Google AI Platform", "Lambda", "Serverless", "Cloud Functions"
    ],
    
    "DevOps": [
        "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions", "Travis CI",
        "CircleCI", "Ansible", "Terraform", "Infrastructure as Code"
    ],
    
    "Database": [
        "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Cassandra", "Redis",
        "Elasticsearch", "Neo4j", "Graph Database", "Database Design", "Query Optimization"
    ],
    
    "Software Engineering": [
        "Software Development", "Object-Oriented Programming", "Functional Programming",
        "Microservices", "API Design", "RESTful Services", "GraphQL", "gRPC",
        "Design Patterns", "System Design", "Scalability", "Testing", "TDD", "BDD"
    ]
}

def create_skills_index():
    """
    Create a flat skill index with related skills for faster matching.
    """
    skill_index = {}
    
    for category, skills in SKILLS_RELATIONSHIPS.items():
        # Add category itself as a skill
        skill_index[category.lower()] = {
            "category": category,
            "related_skills": skills
        }
        
        # Add each skill in the category
        for skill in skills:
            skill_index[skill.lower()] = {
                "category": category,
                "related_skills": [s for s in skills if s != skill] + [category]
            }
    
    # Save the index for faster loading
    skills_dir = Path("app/data")
    skills_dir.mkdir(exist_ok=True)
    
    with open(skills_dir / "skills_index.json", "w") as f:
        json.dump(skill_index, f, indent=2)
    
    return skill_index

def get_skills_index():
    """
    Get or create the skills index.
    """
    skills_path = Path("app/data/skills_index.json")
    
    if skills_path.exists():
        with open(skills_path, "r") as f:
            return json.load(f)
    else:
        return create_skills_index()

def get_related_skills(skill_name):
    """
    Get related skills for a given skill name.
    """
    skill_index = get_skills_index()
    skill_name_lower = skill_name.lower()
    
    # Check for exact match
    if skill_name_lower in skill_index:
        return skill_index[skill_name_lower]
    
    # Check for partial matches
    partial_matches = []
    for indexed_skill in skill_index:
        if skill_name_lower in indexed_skill or indexed_skill in skill_name_lower:
            partial_matches.append(skill_index[indexed_skill])
    
    if partial_matches:
        # Return the first partial match
        return partial_matches[0]
    
    # No match found
    return {
        "category": "Unknown",
        "related_skills": []
    }

def match_skills(resume_skills, job_skills):
    """
    Match resume skills to job skills, considering related skills.
    
    Args:
        resume_skills: List of skills extracted from resume
        job_skills: List of skills required in job description
        
    Returns:
        Dictionary with match results
    """
    skill_index = get_skills_index()
    matches = []
    missing = []
    related_matches = []
    
    # Normalize all skills to lowercase
    resume_skills_lower = [s.lower() for s in resume_skills]
    job_skills_lower = [s.lower() for s in job_skills]
    
    for job_skill in job_skills_lower:
        # Check for direct match
        if job_skill in resume_skills_lower:
            matches.append(job_skill)
            continue
            
        # Check if any related skill is in resume
        related_info = get_related_skills(job_skill)
        related_skills_lower = [s.lower() for s in related_info.get("related_skills", [])]
        
        found_related = False
        matched_related = []
        
        for related_skill in related_skills_lower:
            if related_skill in resume_skills_lower:
                found_related = True
                matched_related.append(related_skill)
        
        if found_related:
            related_matches.append({
                "job_skill": job_skill,
                "matched_via": matched_related
            })
        else:
            missing.append(job_skill)
    
    # Calculate percentage match
    total_job_skills = len(job_skills_lower)
    direct_matches = len(matches)
    related_matches_count = len(related_matches)
    
    # Direct matches count 100%, related matches count 75%
    match_percentage = ((direct_matches + (related_matches_count * 0.75)) / total_job_skills) * 100 if total_job_skills > 0 else 0
    
    return {
        "match_percentage": round(match_percentage, 1),
        "direct_matches": matches,
        "related_matches": related_matches,
        "missing_skills": missing
    }