"""
System Settings model for global configuration.
"""
from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base


class SystemSettings(Base):
    """Global system settings managed by the Super Admin."""
    __tablename__ = "system_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False) # e.g. "AI_CONFIG"
    value = Column(JSON, default={}) # Stores keys like {"google_api_key": "...", "openai_key": "..."}
    description = Column(String(255))
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSettings key={self.key}>"


class AiUsageLog(Base):
    """Log for tracking AI usage and credit consumption."""
    __tablename__ = "ai_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_name = Column(String(100))
    action = Column(String(100))
    credits_consumed = Column(Float, default=0.0)
    request_payload = Column(JSON, nullable=True) # Optional: track what was asked
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AiUsageLog company={self.company_id} user={self.user_id} credits={self.credits_consumed}>"
