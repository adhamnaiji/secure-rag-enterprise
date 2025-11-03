# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Configuration
    API_TITLE: str = "Secure Enterprise RAG System"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "llama3"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    # Vector Database
    VECTOR_DB: str = "faiss"  # faiss, pinecone, milvus
    VECTOR_DIMENSION: int = 1536
    
    # Security Settings
    ENABLE_ENCRYPTION: bool = True
    ENCRYPTION_KEY: Optional[str] = None
    MAX_REQUESTS_PER_MINUTE: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # Compliance
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_PATH: str = "logs/audit.log"
    GDPR_MODE: bool = True  # Automatic data deletion
    
    # Energy Monitoring
    TRACK_ENERGY: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///app.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
