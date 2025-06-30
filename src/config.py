"""Configuration module for the document translation pipeline."""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('config.env')

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for Azure OpenAI and pipeline settings."""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    
    # Pipeline Configuration
    INPUT_DIR: str = "input"
    OUTPUT_DIR: str = "output"
    TEMP_DIR: str = "temp"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required_fields = [
            cls.AZURE_OPENAI_API_KEY,
            cls.AZURE_OPENAI_ENDPOINT,
            cls.AZURE_OPENAI_DEPLOYMENT_NAME
        ]
        return all(field.strip() for field in required_fields)
    
    @classmethod
    def setup_azure_environment(cls):
        """Setup Azure OpenAI environment variables for CrewAI."""
        os.environ["AZURE_OPENAI_API_KEY"] = cls.AZURE_OPENAI_API_KEY
        os.environ["AZURE_API_BASE"] = cls.AZURE_OPENAI_ENDPOINT
        os.environ["AZURE_API_VERSION"] = cls.AZURE_OPENAI_API_VERSION
        logger.info("Azure OpenAI environment variables configured")
    
    @classmethod
    def get_azure_openai_config(cls) -> dict:
        """Get Azure OpenAI configuration as a dictionary."""
        return {
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "azure_deployment": cls.AZURE_OPENAI_DEPLOYMENT_NAME,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS
        } 