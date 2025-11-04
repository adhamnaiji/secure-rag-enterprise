from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Configuration
    API_TITLE: str = "Secure Enterprise RAG System"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ===== LLM Configuration - PERPLEXITY =====
    # NEVER hardcode API keys - use .env file instead
    PERPLEXITY_API_KEY: Optional[str] = None  # ✅ Load from .env
    PERPLEXITY_MODEL: str = "sonar"
    
    # Alternative LLMs (optional)
    GROQ_API_KEY: Optional[str] = None  # ✅ Load from .env
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    GEMINI_API_KEY: Optional[str] = None  # ✅ Load from .env
    GEMINI_MODEL: str = "gemini-pro"
    
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    # ===== Vector Database - QDRANT =====
    QDRANT_URL: str = ":memory:"  # Default to in-memory
    QDRANT_API_KEY: Optional[str] = None  # ✅ Load from .env
    QDRANT_TIMEOUT: int = 60
    COLLECTION_NAME: str = "elearning_courses"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Vector Store (use Qdrant instead of FAISS)
    VECTOR_DB: str = "qdrant"
    VECTOR_DIMENSION: int = 1536
    
    # ===== Security Settings =====
    ENABLE_ENCRYPTION: bool = True
    ENCRYPTION_KEY: str = "your-encryption-key-12345"  # Change in production
    MAX_REQUESTS_PER_MINUTE: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # ===== Compliance =====
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_PATH: str = "logs/audit.log"
    GDPR_MODE: bool = True
    
    # ===== Energy Monitoring =====
    TRACK_ENERGY: bool = True
    
    # ===== Database =====
    DATABASE_URL: str = "sqlite:///app.db"
    
    # ===== Server =====
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:4200"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
