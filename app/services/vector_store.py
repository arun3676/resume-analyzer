"""
Vector store service for ChromaDB integration.
"""
from typing import List, Dict, Any
import os
import json
import chromadb
from chromadb.config import Settings

from app.config import CHROMA_PERSIST_DIRECTORY, COLLECTION_NAME

def initialize_vector_store():
    """
    Initialize the ChromaDB vector store.
    """
    # Create the directory if it doesn't exist
    os.makedirs(CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    
    # Initialize the client
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIRECTORY,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create the collection
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as e:  # Change this line to catch all exceptions
        # Collection doesn't exist, create it
        collection = client.create_collection(COLLECTION_NAME)
        
        # Populate with some initial data (in a real app, this would be more extensive)
        populate_initial_data(collection)
    
    return collection

def populate_initial_data(collection):
    """
    Populate the vector store with initial data.
    """
    # Add common skills with related skills
    skills_data = [
        {
            "skill": "Python",
            "related_skills": "NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch, Django, Flask",
            "category": "Programming Language"
        },
        {
            "skill": "Machine Learning",
            "related_skills": "Deep Learning, Neural Networks, NLP, Computer Vision, Regression, Classification",
            "category": "AI/Data Science"
        },
        {
            "skill": "AWS",
            "related_skills": "EC2, S3, Lambda, DynamoDB, CloudFormation, SageMaker",
            "category": "Cloud"
        },
        {
            "skill": "Docker",
            "related_skills": "Kubernetes, Containerization, Microservices, CI/CD, DevOps",
            "category": "DevOps"
        },
        {
            "skill": "JavaScript",
            "related_skills": "TypeScript, React, Angular, Vue.js, Node.js, Express.js",
            "category": "Web Development"
        }
    ]
    
    # Add industry standards
    industry_standards = [
        {
            "industry": "Software Engineering",
            "standards": "Clean, ATS-friendly format. Include: languages, frameworks, methodologies. Highlight metrics and achievements. Include GitHub, personal projects."
        },
        {
            "industry": "Data Science",
            "standards": "Lead with technical skills (Python, R, ML libraries). Highlight impactful projects with measurable results. Include domain expertise and visualization skills."
        },
        {
            "industry": "Cloud Engineering",
            "standards": "Focus on cloud platforms (AWS/Azure/GCP), certifications, infrastructure as code, security, and cost optimization experience. Include architecture diagrams if possible."
        },
        {
            "industry": "Full Stack Development",
            "standards": "Balance frontend and backend skills. Show end-to-end project experience. Highlight performance optimization, responsive design, and API development."
        }
    ]
    
    # Add to collection
    collection.add(
        documents=[json.dumps(item) for item in skills_data],
        metadatas=[{"type": "skill_data"} for _ in skills_data],
        ids=[f"skill_{i}" for i in range(len(skills_data))]
    )
    
    collection.add(
        documents=[json.dumps(item) for item in industry_standards],
        metadatas=[{"type": "industry_standard"} for _ in industry_standards],
        ids=[f"industry_{i}" for i in range(len(industry_standards))]
    )

def get_similar_skills(skill: str) -> Dict[str, Any]:
    """
    Find similar or related skills for a given skill.
    
    Args:
        skill: The skill to find related skills for
        
    Returns:
        Dictionary with related skills information
    """
    collection = initialize_vector_store()
    
    # Query the collection for similar skills
    results = collection.query(
        query_texts=[skill],
        n_results=1,
        where={"type": "skill_data"}
    )
    
    if not results["documents"] or not results["documents"][0]:
        return {
            "skill": skill,
            "related_skills": [],
            "message": "No related skills found for this skill"
        }
    
    # Parse the result
    skill_data = json.loads(results["documents"][0][0])
    
    related_skills = [s.strip() for s in skill_data.get("related_skills", "").split(",")]
    
    return {
        "skill": skill_data.get("skill", skill),
        "related_skills": related_skills,
        "category": skill_data.get("category", "Unknown")
    }

def get_industry_standards(industry: str) -> Dict[str, Any]:
    """
    Get industry standards for resumes in a specific field.
    
    Args:
        industry: The industry to get standards for
        
    Returns:
        Dictionary with industry standards information
    """
    collection = initialize_vector_store()
    
    # Query the collection for industry standards
    results = collection.query(
        query_texts=[industry],
        n_results=1,
        where={"type": "industry_standard"}
    )
    
    if not results["documents"] or not results["documents"][0]:
        return {
            "industry": industry,
            "standards": "No specific standards found for this industry",
            "message": "Consider using general professional resume standards"
        }
    
    # Parse the result
    industry_data = json.loads(results["documents"][0][0])
    
    return {
        "industry": industry_data.get("industry", industry),
        "standards": industry_data.get("standards", "No specific standards found")
    }