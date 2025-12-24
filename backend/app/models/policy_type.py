"""
Policy Type model for different insurance types.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class PolicyType(Base):
    """Policy Type model for insurance products."""
    __tablename__ = "policy_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)  # 'Vehicle', 'Property', etc.
    code = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    quotes = relationship("Quote", back_populates="policy_type", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="policy_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PolicyType {self.name}>"
