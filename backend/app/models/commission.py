"""
Commission model for tracking agent/broker earnings.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base


class Commission(Base):
    """Commission model."""
    __tablename__ = "commissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"))
    
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(50), default='pending')  # 'pending', 'paid', 'canceled'
    paid_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    agent = relationship("User")
    policy = relationship("Policy")

    def __repr__(self):
        return f"<Commission {self.amount} for {self.agent_id}>"
