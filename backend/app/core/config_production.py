"""
Production configuration for Tinsur-AI.
This extends the base config with production-specific hardening.
"""
from typing import List, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os
import secrets

class ProductionSettings(BaseSettings):
    """Production-hardened application settings."""
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Application
    APP_NAME: str = "Tinsur.AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # PRODUCTION: Always False
    ENVIRONMENT: str = "production"  # PRODUCTION: Always production
    
    # Database - PostgreSQL recommended for production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/tinsur_ai"
    )
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017/insurance_saas_logs"
    )
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # Security - MUST be configured via environment variables in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production!")
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Internal API Key
    A2A_INTERNAL_API_KEY: str = os.getenv("A2A_INTERNAL_API_KEY", "")
    if not A2A_INTERNAL_API_KEY:
        raise ValueError("A2A_INTERNAL_API_KEY environment variable must be set!")
    
    # External API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    FACEBOOK_APP_ID: str = os.getenv("FACEBOOK_APP_ID", "")
    FACEBOOK_APP_SECRET: str = os.getenv("FACEBOOK_APP_SECRET", "")
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID", "")
    APPLE_TEAM_ID: str = os.getenv("APPLE_TEAM_ID", "")
    APPLE_KEY_ID: str = os.getenv("APPLE_KEY_ID", "")
    APPLE_PRIVATE_KEY: str = os.getenv("APPLE_PRIVATE_KEY", "")

    # CORS - Restrict to specific domains in production
    ALLOWED_ORIGINS: Any = os.getenv(
        "ALLOWED_ORIGINS",
        "https://tinsur.example.com,https://admin.tinsur.example.com"
    )
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from various formats."""
        if isinstance(v, str) and not v.startswith("["):
            origins = [i.strip() for i in v.split(",")]
            # PRODUCTION: Never allow wildcard
            if "*" in origins:
                raise ValueError("Wildcard CORS origins not allowed in production!")
            return origins
        elif isinstance(v, list):
            if "*" in v:
                raise ValueError("Wildcard CORS origins not allowed in production!")
            return v
        return []
    
    # File Storage
    UPLOAD_DIR: str = "/var/tinsur-ai/uploads"  # Use absolute path in production
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    # Logging - Production level
    LOG_LEVEL: str = "WARNING"
    LOG_FILE: str = "/var/log/tinsur-ai/app.log"
    
    # Monitoring & Error Tracking
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of transactions
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # per period
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour
    
    # Security Headers
    SECURE_HSTS_SECONDS: int = 31536000  # 1 year
    SECURE_SSL_REDIRECT: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Strict"
    CSRF_COOKIE_SECURE: bool = True
    CSRF_COOKIE_HTTPONLY: bool = True
    
    # Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM UTC
    BACKUP_RETENTION_DAYS: int = 30
    
    # Connection Pool
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0  # Strict - no overflow connections
    DB_POOL_PRE_PING: bool = True  # Test connections before use
    
    model_config = SettingsConfigDict(
        env_file=".env.production",
        case_sensitive=True,
        extra="ignore"
    )

    @classmethod
    def validate_production_requirements(cls):
        """Validate all production requirements are met."""
        errors = []
        
        # Check critical env vars
        if not os.getenv("SECRET_KEY"):
            errors.append("SECRET_KEY not set")
        if not os.getenv("A2A_INTERNAL_API_KEY"):
            errors.append("A2A_INTERNAL_API_KEY not set")
        
        # Check database URL
        db_url = os.getenv("DATABASE_URL", "")
        if "localhost" in db_url or "127.0.0.1" in db_url:
            errors.append("DATABASE_URL points to localhost (use production database)")
        
        if errors:
            raise ValueError(f"Production requirements not met: {'; '.join(errors)}")


# Global production settings instance
# This will fail fast if production requirements aren't met
try:
    settings = ProductionSettings()
    ProductionSettings.validate_production_requirements()
except ValueError as e:
    print(f"FATAL: Production configuration error: {e}")
    raise
