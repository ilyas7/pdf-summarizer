# src/config.py
"""Configuration management for PDF Summarizer."""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    OUTPUT_DIR = DATA_DIR / "outputs"
    KNOWLEDGE_DIR = OUTPUT_DIR / "knowledge_bases"
    SUMMARIES_DIR = OUTPUT_DIR / "summaries"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    ANALYSIS_MODEL: str = os.getenv("ANALYSIS_MODEL", "gpt-3.5-turbo")
    
    # Processing Configuration
    ANALYSIS_INTERVAL: int = int(os.getenv("ANALYSIS_INTERVAL", "10"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    MAX_PAGES: Optional[int] = os.getenv("MAX_PAGES")
    if MAX_PAGES:
        MAX_PAGES = int(MAX_PAGES)
    
    # Streamlit Configuration
    PORT: int = int(os.getenv("PORT", "8080"))
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "false").lower() == "true"
    ENABLE_XSRF: bool = os.getenv("ENABLE_XSRF", "false").lower() == "true"
    
    @classmethod
    def setup_directories(cls) -> None:
        """Create all necessary directories."""
        directories = [
            cls.UPLOAD_DIR,
            cls.KNOWLEDGE_DIR,
            cls.SUMMARIES_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        return True

# Initialize directories on import
Config.setup_directories()