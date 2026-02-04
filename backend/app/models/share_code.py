"""
ShareCode model for document sharing authorization.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base
from app.core.time import utcnow

class ShareCode(Base):
    """ShareCode model for generating secure sharing codes."""
    __tablename__ = "share_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # B2B, B2C, B2E, E2C, E2E, C2C
    share_type = Column(String(10), nullable=False)
    
    # List of recipient IDs (User IDs or Client IDs depending on share_type)
    recipient_ids = Column(JSON, nullable=False, default=list)
    
    status = Column(String(20), default="active") # active, revoked, used
    
    # For potential QR code storage or just on-the-fly generation
    # Storing base64 string might be too heavy, better to generate on fly or store URL if uploaded
    # For now, we'll generate it on the fly in the endpoint response.
    
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    creator = relationship("User", backref="share_codes")
    
    def __repr__(self):
        return f"<ShareCode {self.code}>"
