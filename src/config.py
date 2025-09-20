"""Configuration module for the document translation pipeline."""

import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('config.env')

logger = logging.getLogger(__name__)

class FontConfig:
    """Font configuration with language-specific preferences and fallbacks."""
    
    # Language-specific font preferences with comprehensive fallbacks
    LANGUAGE_FONTS: Dict[str, Dict[str, List[str]]] = {
        "chinese_simplified": {
            "primary": ["Microsoft YaHei", "SimSun", "SimHei"],
            "fallback": ["Arial Unicode MS", "Segoe UI", "Arial"],
            "description": "Simplified Chinese fonts with complete character coverage"
        },
        "chinese_traditional": {
            "primary": ["Microsoft JhengHei", "MingLiU", "PMingLiU"],
            "fallback": ["Arial Unicode MS", "Segoe UI", "Arial"],
            "description": "Traditional Chinese fonts"
        },
        "japanese": {
            "primary": ["Meiryo", "MS Gothic", "Yu Gothic"],
            "fallback": ["Arial Unicode MS", "Segoe UI", "Arial"],
            "description": "Japanese fonts supporting Hiragana, Katakana, and Kanji"
        },
        "korean": {
            "primary": ["Malgun Gothic", "Batang", "Dotum"],
            "fallback": ["Arial Unicode MS", "Segoe UI", "Arial"],
            "description": "Korean fonts with Hangul support"
        },
        "thai": {
            "primary": ["Angsana New", "Cordia New", "Tahoma"],
            "fallback": ["Arial Unicode MS", "Segoe UI", "Arial"],
            "description": "Thai fonts with proper character rendering"
        },
        "hindi": {
            "primary": ["Mangal", "Devanagari Sangam MN", "Nirmala UI"],
            "fallback": ["Arial Unicode MS", "Segoe UI", "Arial"],
            "description": "Hindi/Devanagari script fonts"
        },
        "russian": {
            "primary": ["Times New Roman", "Arial", "Calibri"],
            "fallback": ["Segoe UI", "Tahoma", "Arial Unicode MS"],
            "description": "Cyrillic script support"
        },
        "spanish": {
            "primary": ["Arial", "Calibri", "Times New Roman"],
            "fallback": ["Segoe UI", "Tahoma", "Helvetica"],
            "description": "Latin script with accent support"
        },
        "french": {
            "primary": ["Arial", "Calibri", "Times New Roman"],
            "fallback": ["Segoe UI", "Tahoma", "Helvetica"],
            "description": "French with proper accent and ligature support"
        },
        "german": {
            "primary": ["Arial", "Calibri", "Times New Roman"],
            "fallback": ["Segoe UI", "Tahoma", "Helvetica"],
            "description": "German with umlaut support"
        },
        "english": {
            "primary": ["Arial", "Calibri", "Times New Roman"],
            "fallback": ["Segoe UI", "Tahoma", "Helvetica"],
            "description": "Standard English fonts"
        }
    }
    
    # Universal fallback fonts with broad language support
    UNIVERSAL_FALLBACKS = [
        "Arial Unicode MS",  # Comprehensive Unicode support
        "Segoe UI",         # Modern Windows UI font
        "Tahoma",           # Good Unicode fallback
        "Arial",            # Standard fallback
        "sans-serif"        # Generic fallback
    ]
    
    
    @classmethod
    def get_font_stack(cls, language: str, document_type: str = "professional") -> List[str]:
        """
        Get complete font stack for a language with fallbacks.
        
        Args:
            language: Target language code
            document_type: Type of document (affects font selection)
        
        Returns:
            Complete font stack with primary fonts and fallbacks
        """
        language_key = language.lower().replace("-", "_")
        
        if language_key in cls.LANGUAGE_FONTS:
            fonts = cls.LANGUAGE_FONTS[language_key]
            font_stack = fonts["primary"] + fonts["fallback"]
        else:
            # Use English fonts as default with universal fallbacks
            font_stack = cls.LANGUAGE_FONTS["english"]["primary"] + cls.UNIVERSAL_FALLBACKS
        
        # Remove duplicates while preserving order
        seen = set()
        unique_fonts = []
        for font in font_stack:
            if font not in seen:
                seen.add(font)
                unique_fonts.append(font)
        
        return unique_fonts
    
    @classmethod
    def get_primary_font(cls, language: str) -> str:
        """Get the primary font for a language."""
        language_key = language.lower().replace("-", "_")
        
        if language_key in cls.LANGUAGE_FONTS:
            return cls.LANGUAGE_FONTS[language_key]["primary"][0]
        else:
            return cls.LANGUAGE_FONTS["english"]["primary"][0]
    
    
    @classmethod
    def get_language_info(cls, language: str) -> Dict[str, any]:
        """Get comprehensive language information including fonts and direction."""
        language_key = language.lower().replace("-", "_")
        
        font_info = cls.LANGUAGE_FONTS.get(language_key, cls.LANGUAGE_FONTS["english"])
        
        return {
            "language": language,
            "writing_direction": "ltr",  # All languages are LTR now
            "primary_fonts": font_info["primary"],
            "fallback_fonts": font_info["fallback"],
            "font_stack": cls.get_font_stack(language),
            "primary_font": cls.get_primary_font(language),
            "description": font_info["description"]
        }

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