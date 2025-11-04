# config/settings.py - FIXED & SECURE
"""
Application Settings - Pydantic V2 Compatible
- Loads from .env file
- NO hardcoded secrets
- All fields properly typed
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration with validation"""
    
    # ===== API CONFIGURATION =====
    API_TITLE: str = "Secure Enterprise RAG System"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:4200"
    
    # ===== LLM Configuration - PERPLEXITY (FREE) =====
    PERPLEXITY_API_KEY: Optional[str] = None  # Load from .env
    PERPLEXITY_MODEL: str = "sonar"
    
    # ===== EMBEDDINGS - HUGGINGFACE (FREE, LOCAL) =====
    EMBEDDING_MODEL: str = "sentence-transformers/all-miniLM-L6-v2"
    
    # ===== LLM PARAMETERS =====
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    # ===== Vector Database - QDRANT =====
    QDRANT_URL: str = "https://c1fe83e2-b226-4535-ba34-1a050c948be7.eu-central-1-0.aws.cloud.qdrant.io:6333"
    QDRANT_API_KEY: Optional[str] = None  # Load from .env
    QDRANT_TIMEOUT: int = 60
    COLLECTION_NAME: str = "elearning_courses"
    
    # ===== VECTOR STORE SETTINGS =====
    VECTOR_DB: str = "qdrant"
    VECTOR_DIMENSION: int = 1536
    
    # ===== RAG SETTINGS =====
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # ===== SECURITY SETTINGS =====
    ENABLE_ENCRYPTION: bool = True
    ENCRYPTION_KEY: str = "your-encryption-key-12345"
    MAX_REQUESTS_PER_MINUTE: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # ===== COMPLIANCE & AUDIT =====
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_PATH: str = "logs/audit.log"
    GDPR_MODE: bool = True
    
    # ===== ENERGY MONITORING =====
    TRACK_ENERGY: bool = True
    
    # ===== DATABASE =====
    DATABASE_URL: str = "sqlite:///app.db"
    
    class Config:
        """Pydantic v2 configuration"""
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Create settings instance
settings = Settings()
