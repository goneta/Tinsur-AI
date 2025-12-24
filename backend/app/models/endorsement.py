"""
Endorsement model for policy modifications.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Date, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Endorsement(Base):
    """Endorsement model for mid-term policy adjustments."""
    __tablename__ = "endorsements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"))
    
    # Endorsement details
    endorsement_number = Column(String(50), unique=True, nullable=False)
    endorsement_type = Column(String(50), nullable=False)  # 'coverage_change', 'beneficiary_change', 'premium_adjustment', 'term_extension'
    
    # Dates
    effective_date = Column(Date, nullable=False)
    issued_date = Column(Date, default=datetime.utcnow)
    
    # Changes
    changes = Column(JSON, default={})  # Detailed changes made
    reason = Column(Text)
    
    # Financial impact
    premium_adjustment = Column(Numeric(15, 2), default=0)  # Positive = increase, Negative = decrease
    new_premium = Column(Numeric(15, 2))
    
    # Status
    status = Column(String(50), default='draft')  # 'draft', 'pending_approval', 'approved', 'rejected', 'active'
    
    # Documents
    document_url = Column(String(500))
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    policy = relationship("Policy", back_populates="endorsements")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Endorsement {self.endorsement_number} - {self.status}>"
