"""
Logging service for PromptLayer integration.
"""
import promptlayer
import logging
from typing import Dict, Any, Optional

from app.config import PROMPTLAYER_API_KEY

# Configure logging - REMOVED basicConfig
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )

logger = logging.getLogger(__name__)

def initialize_promptlayer():
    """Initialize PromptLayer for logging."""
    # PromptLayer disabled for this project
    logger.info("PromptLayer logging disabled.")
    return False

def log_prompt(
    provider: str,
    model: str,
    prompt: str,
    response: str,
    tags: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Log a prompt to PromptLayer.
    
    Args:
        provider: The provider (e.g., "openai")
        model: The model name
        prompt: The prompt text
        response: The response text
        tags: Optional list of tags
        metadata: Optional metadata dictionary
    """
    if not PROMPTLAYER_API_KEY:
        return
    
    try:
        promptlayer.track.prompt(
            provider=provider,
            model=model,
            prompt=prompt,
            response=response,
            tags=tags or [],
            metadata=metadata or {}
        )
        logger.info(f"Logged prompt to PromptLayer with tags: {tags}")
    except Exception as e:
        logger.error(f"Failed to log prompt to PromptLayer: {str(e)}")