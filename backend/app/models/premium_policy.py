"""
Premium Policy models for complex eligibility rules and pricing.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Numeric, Table
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
import uuid
from datetime import datetime

from app.core.database import Base

# Association table for PremiumPolicyType and PremiumPolicyCriteria
premium_policy_type_criteria = Table(
    "premium_policy_type_criteria",
    Base.metadata,
    Column("policy_type_id", GUID(), ForeignKey("premium_policy_types.id", ondelete="CASCADE"), primary_key=True),
    Column("criteria_id", GUID(), ForeignKey("premium_policy_criteria.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for PremiumPolicyType and PolicyService
premium_policy_service_association = Table(
    "premium_policy_service_association",
    Base.metadata,
    Column("policy_type_id", GUID(), ForeignKey("premium_policy_types.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", GUID(), ForeignKey("policy_services.id", ondelete="CASCADE"), primary_key=True),
)

class PremiumPolicyCriteria(Base):
    """Criteria for premium policy eligibility."""
    __tablename__ = "premium_policy_criteria"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    field_name = Column(String(100), nullable=False)  # e.g., 'car_age', 'accidents_not_fault'
    operator = Column(String(20), nullable=False)    # e.g., '<', '>', '=', 'between'
    value = Column(String(255), nullable=False)      # e.g., '5', '0,1'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company")
    policy_types = relationship("PremiumPolicyType", secondary=premium_policy_type_criteria, back_populates="criteria")

class PremiumPolicyType(Base):
    """Premium Policy Type with pricing and eligibility rules."""
    __tablename__ = "premium_policy_types"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(15, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company")
    company = relationship("Company")
    criteria = relationship("PremiumPolicyCriteria", secondary=premium_policy_type_criteria, back_populates="policy_types")
    services = relationship("PolicyService", secondary=premium_policy_service_association)

    def __repr__(self):
        return f"<PremiumPolicyType {self.name}>"
