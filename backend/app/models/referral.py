"""
Referral model for tracking client referrals.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base
from app.core.guid import GUID
from app.core.time import utcnow

class Referral(Base):
    """Referral model."""
    __tablename__ = "referrals"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    referrer_client_id = Column(GUID(), ForeignKey("clients.id", ondelete="SET NULL"))
    referred_client_id = Column(GUID(), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    
    referral_code = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default='pending') # 'pending', 'converted', 'expired'
    
    reward_amount = Column(Numeric(10, 2))
    reward_paid = Column(Boolean, default=False)
    
    converted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    company = relationship("Company")
    referrer = relationship("Client", foreign_keys=[referrer_client_id])
    referred = relationship("Client", foreign_keys=[referred_client_id])
    
    def __repr__(self):
        return f"<Referral {self.referral_code}>"
