"""
User Settings model for storing user preferences.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base


class Settings(Base):
    """User settings model for theme, language, and other preferences."""
    __tablename__ = "settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Appearance
    theme = Column(String(20), default="light")  # 'light' or 'dark'
    language = Column(String(10), default="en")  # 'en', 'fr', 'es'
    
    # Regional
    timezone = Column(String(50), default="UTC")
    date_format = Column(String(50), default="MM/DD/YYYY")
    currency_format = Column(String(10), default="USD")
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    user = relationship("User", backref="settings")
    
    def __repr__(self):
        return f"<Settings user_id={self.user_id} theme={self.theme} language={self.language}>"
