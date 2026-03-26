"""
Model for storing agent long-term memories and conversation state.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class AgentMemory(Base):
    """Model for storing agent long-term memories and conversation state."""
    __tablename__ = "agent_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    agent_id = Column(String(255), nullable=False) # Name of the agent (e.g., 'quote_agent')
    memory_key = Column(String(255), nullable=False) # Unique key for the memory (e.g., 'user_preference')
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True) # Renamed to avoid reserved words if any, though JSON is fine
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<AgentMemory {self.agent_id}:{self.memory_key} for {self.user_id}>"
