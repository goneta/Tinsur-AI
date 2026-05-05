"""
Core configuration for the Insurance SaaS Platform.
"""
from typing import List, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os
import secrets

class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",        # 👈 THIS is the key fix
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    
    # Application
    APP_NAME: str = "Tinsur.AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    ENABLE_DEV_ENDPOINTS: bool = False
    REQUEST_ID_HEADER: str = "X-Request-ID"
    
    # Database
    DATABASE_URL: str 
    MONGODB_URL: str = "mongodb://localhost:27017/insurance_saas_logs"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    A2A_INTERNAL_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FACEBOOK_APP_ID: str = os.getenv("NEXT_PUBLIC_FACEBOOK_APP_ID", "")
    FACEBOOK_APP_SECRET: str = ""
    APPLE_CLIENT_ID: str = ""
    APPLE_TEAM_ID: str = ""
    APPLE_KEY_ID: str = ""
    APPLE_PRIVATE_KEY: str = os.getenv("APPLE_PRIVATE_KEY", "")

    
    # CORS
    ALLOWED_ORIGINS: Any = "http://localhost:3000,http://127.0.0.1:3000"

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def ensure_secret_key(cls, v: str) -> str:
        """Generate a secure random SECRET_KEY if not set or using default."""
        if not v or v == "dev_secret_key_123456789":
            import warnings
            warnings.warn("SECRET_KEY not set! Generating a random key. Set SECRET_KEY in .env for production.", stacklevel=2)
            return secrets.token_urlsafe(64)
        return v

    @field_validator("A2A_INTERNAL_API_KEY", mode="before")
    @classmethod
    def ensure_a2a_key(cls, v: str) -> str:
        """Generate a secure random A2A_INTERNAL_API_KEY if not set or using default."""
        if not v or v == "super-secret-a2a-key":
            return secrets.token_urlsafe(32)
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from various formats."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
