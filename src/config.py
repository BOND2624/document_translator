"""Configuration module for the document translation pipeline."""

import os
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import logging

# Load environment variables from multiple possible locations
load_dotenv('.env')  # Load from .env first
load_dotenv('config.env')  # Then load from config.env if it exists (will override .env)

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
    """Configuration class for multiple LLM providers and pipeline settings."""
    
    # LLM Provider Selection
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")  # groq, azure, openrouter
    
    # Groq Configuration (FREE)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Azure OpenAI Configuration (PAID)
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    
    # OpenRouter Configuration (FREE TIER)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
    
    # Model Configuration
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    
    # Pipeline Configuration
    INPUT_DIR: str = "input"
    OUTPUT_DIR: str = "output"
    TEMP_DIR: str = "temp"
    
    # Available LLM Providers
    AVAILABLE_PROVIDERS = {
        "groq": {
            "name": "Groq",
            "cost": "FREE",
            "models": ["llama-3.3-70b-versatile", "llama-3.2-90b-text-preview", "mixtral-8x7b-32768", "gemma2-9b-it"],
            "speed": "Very Fast",
            "description": "Fast and free Llama models"
        },
        "openrouter": {
            "name": "OpenRouter", 
            "cost": "FREE Tier",
            "models": ["meta-llama/llama-3.1-8b-instruct:free", "microsoft/phi-3-medium-128k-instruct:free"],
            "speed": "Fast",
            "description": "Free tier with various models"
        },
        "azure": {
            "name": "Azure OpenAI",
            "cost": "PAID",
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "speed": "Medium",
            "description": "Premium GPT models"
        }
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present for selected provider."""
        provider = cls.LLM_PROVIDER.lower()
        
        if provider == "groq":
            return bool(cls.GROQ_API_KEY.strip())
        elif provider == "azure":
            required_fields = [
                cls.AZURE_OPENAI_API_KEY,
                cls.AZURE_OPENAI_ENDPOINT,
                cls.AZURE_OPENAI_DEPLOYMENT_NAME
            ]
            return all(field.strip() for field in required_fields)
        elif provider == "openrouter":
            return bool(cls.OPENROUTER_API_KEY.strip())
        else:
            return False
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration for the selected provider."""
        provider = cls.LLM_PROVIDER.lower()
        
        if provider == "groq":
            return {
                "provider": "groq",
                "api_key": cls.GROQ_API_KEY,
                "model": cls.GROQ_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS
            }
        elif provider == "azure":
            return {
                "provider": "azure",
                "api_key": cls.AZURE_OPENAI_API_KEY,
                "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
                "api_version": cls.AZURE_OPENAI_API_VERSION,
                "azure_deployment": cls.AZURE_OPENAI_DEPLOYMENT_NAME,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS
            }
        elif provider == "openrouter":
            return {
                "provider": "openrouter",
                "api_key": cls.OPENROUTER_API_KEY,
                "model": cls.OPENROUTER_MODEL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @classmethod
    def setup_environment(cls):
        """Setup environment variables for the selected LLM provider."""
        provider = cls.LLM_PROVIDER.lower()
        
        if provider == "groq":
            os.environ["GROQ_API_KEY"] = cls.GROQ_API_KEY
            logger.info("Groq environment variables configured")
        elif provider == "azure":
            os.environ["AZURE_OPENAI_API_KEY"] = cls.AZURE_OPENAI_API_KEY
            os.environ["AZURE_API_BASE"] = cls.AZURE_OPENAI_ENDPOINT
            os.environ["AZURE_API_VERSION"] = cls.AZURE_OPENAI_API_VERSION
            logger.info("Azure OpenAI environment variables configured")
        elif provider == "openrouter":
            os.environ["OPENROUTER_API_KEY"] = cls.OPENROUTER_API_KEY
            logger.info("OpenRouter environment variables configured")
    
    @classmethod
    def get_provider_info(cls) -> dict:
        """Get information about the current provider."""
        provider = cls.LLM_PROVIDER.lower()
        return cls.AVAILABLE_PROVIDERS.get(provider, {})
    
    # Legacy methods for backward compatibility
    @classmethod
    def get_azure_openai_config(cls) -> dict:
        """Legacy method - use get_llm_config() instead."""
        if cls.LLM_PROVIDER.lower() == "azure":
            return cls.get_llm_config()
        else:
            raise ValueError("Azure OpenAI not configured as current provider")
    
    @classmethod
    def setup_azure_environment(cls):
        """Legacy method - use setup_environment() instead."""
        if cls.LLM_PROVIDER.lower() == "azure":
            cls.setup_environment()
        else:
            logger.warning("Azure OpenAI not configured as current provider")
    
    @classmethod
    def create_llm(cls) -> Any:
        """Create an LLM instance based on the configured provider."""
        cls.setup_environment()
        config = cls.get_llm_config()
        provider = config["provider"]
        
        try:
            if provider == "groq":
                from langchain_groq import ChatGroq
                return ChatGroq(
                    api_key=config["api_key"],
                    model=config["model"],
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"]
                )
            elif provider == "azure":
                from langchain_openai import AzureChatOpenAI
                return AzureChatOpenAI(
                    api_key=config["api_key"],
                    azure_endpoint=config["azure_endpoint"],
                    api_version=config["api_version"],
                    azure_deployment=config["azure_deployment"],
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"]
                )
            elif provider == "openrouter":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    api_key=config["api_key"],
                    model=config["model"],
                    base_url="https://openrouter.ai/api/v1",
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"]
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except ImportError as e:
            logger.error(f"Failed to import required package for {provider}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create LLM for {provider}: {e}")
            raise 