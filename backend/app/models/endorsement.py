"""
Endorsement model for policy modifications.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Date, Numeric, Text
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Date, Numeric, Text
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime
from app.core.time import utcnow, utcnow_date

from app.core.database import Base


class Endorsement(Base):
    """Endorsement model for mid-term policy adjustments."""
    __tablename__ = "endorsements"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    policy_id = Column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"))
    
    # Endorsement details
    endorsement_number = Column(String(50), unique=True, nullable=False)
    endorsement_type = Column(String(50), nullable=False)  # 'coverage_change', 'beneficiary_change', 'premium_adjustment', 'term_extension'
    
    # Dates
    effective_date = Column(Date, nullable=False)
    issued_date = Column(Date, default=utcnow_date)
    
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
    approved_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Audit
    created_by = Column(GUID(), ForeignKey("users.id"))
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    policy = relationship("Policy", back_populates="endorsements")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Endorsement {self.endorsement_number} - {self.status}>"
