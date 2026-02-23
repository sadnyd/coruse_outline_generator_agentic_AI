from utils.flow_logger import function_logger
"""
Configuration file for development and production.
"""

import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Environment(str, Enum):
    """Environment modes."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Config:
    """Base configuration."""
    
    ENV = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    
    # LLM Config
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")  # openai, anthropic, local
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # Web Search Config
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    DUCKDUCKGO_ENABLED = os.getenv("DUCKDUCKGO_ENABLED", "true").lower() == "true"
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
    
    # ChromaDB Config
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")
    CHROMA_COLLECTION_NAME = "curricula"
    
    # Session Config
    SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "30"))
    MAX_SESSION_SIZE_MB = int(os.getenv("MAX_SESSION_SIZE_MB", "100"))
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/course_ai_sessions")
    
    # Validator Config
    VALIDATOR_THRESHOLD = float(os.getenv("VALIDATOR_THRESHOLD", "75"))
    MAX_REGENERATION_ATTEMPTS = int(os.getenv("MAX_REGENERATION_ATTEMPTS", "3"))
    
    # Logging Config
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    PII_FILTERING_ENABLED = os.getenv("PII_FILTERING_ENABLED", "true").lower() == "true"
    
    # Streamlit Config
    STREAMLIT_PAGE_ICON = "📚"
    STREAMLIT_LAYOUT = "wide"


class DevelopmentConfig(Config):
    """Development-specific config."""
    
    DEBUG = True
    TESTING = False
    LLM_TEMPERATURE = 0.9  # More creative
    SESSION_TTL_MINUTES = 60


class TestingConfig(Config):
    """Testing-specific config."""
    
    DEBUG = True
    TESTING = True
    LLM_PROVIDER = "mock"  # Use mock LLM
    VALIDATOR_THRESHOLD = 50  # Lower threshold for testing


class ProductionConfig(Config):
    """Production-specific config."""
    
    DEBUG = False
    TESTING = False
    LLM_TEMPERATURE = 0.3  # More deterministic
    SESSION_TTL_MINUTES = 15


# Select config based on environment
@function_logger("Get config")
def get_config():
    """Get config based on ENVIRONMENT variable."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


config = get_config()
