"""
Underwriting models for authority and referrals.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class UnderwritingReferral(Base):
    """
    Tracks quotes that require manual underwriting approval.
    """
    __tablename__ = "underwriting_referrals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=True, unique=True)
    endorsement_id = Column(UUID(as_uuid=True), ForeignKey("endorsements.id", ondelete="CASCADE"), nullable=True, unique=True)
    
    referred_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    status = Column(String(50), default='pending') # 'pending', 'approved', 'rejected'
    reason = Column(String(500)) # e.g., "Exceeds authority limit ($10k)"
    decision_notes = Column(Text)
    
    decided_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    quote = relationship("Quote")
    endorsement = relationship("Endorsement")
    referrer = relationship("User", foreign_keys=[referred_by_id])
    assignee = relationship("User", foreign_keys=[assigned_to_id])
    decider = relationship("User", foreign_keys=[decided_by_id])
