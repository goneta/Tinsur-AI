"""
API Key model for AI Agents.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class ApiKey(Base):
    """API Key model for AI Agents."""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), nullable=False)  # We store the hash, not the key itself
    key_prefix = Column(String(10), nullable=False) # Store first few chars for identification
    name = Column(String(100), nullable=False)      # e.g., "OCR Agent Key"
    agent_id = Column(String(100), nullable=True)   # The ID of the agent this key belongs to
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ApiKey {self.name}>"
