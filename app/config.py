"""
Configuration settings for the Resume Analyzer application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys

PROMPTLAYER_API_KEY = os.getenv("PROMPTLAYER_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-1.5-pro")

# Application settings
APP_NAME = "Resume Analyzer"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# LLM settings
DEFAULT_MODEL = "gemini-1.5-pro"
TEMPERATURE = 0.2
MAX_TOKENS = 4000

# ChromaDB settings
CHROMA_PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma")
COLLECTION_NAME = "resume_knowledge"

# MLflow settings
MLFLOW_TRACKING_URI = "file:" + os.path.join(os.path.dirname(os.path.dirname(__file__)), "mlruns")
EXPERIMENT_NAME = "resume-analyzer"