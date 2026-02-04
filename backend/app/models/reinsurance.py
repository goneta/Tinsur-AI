"""
Reinsurance models.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date, Text, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date
from app.core.time import utcnow

from app.core.database import Base

class ReinsuranceTreaty(Base):
    """
    Represents a reinsurance contract (Treaty).
    """
    __tablename__ = "reinsurance_treaties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    reinsurer_name = Column(String(255), nullable=False)
    treaty_number = Column(String(100), unique=True, nullable=False)
    
    # Quota Share Configuration
    share_percentage = Column(Numeric(5, 2), nullable=False) # e.g., 20.00%
    commission_percentage = Column(Numeric(5, 2), default=0.00) # Commission paid back to insurer
    
    treaty_type = Column(String(50), default='quota_share') # 'quota_share', 'excess_of_loss'
    policy_type_id = Column(UUID(as_uuid=True), ForeignKey("policy_types.id"), nullable=True) # If restricted to one type
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(String(50), default='active') # 'active', 'expired', 'cancelled'
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class ReinsuranceCession(Base):
    """
    Records the premium portion ceded to a reinsurer for a specific policy.
    """
    __tablename__ = "reinsurance_cessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"))
    treaty_id = Column(UUID(as_uuid=True), ForeignKey("reinsurance_treaties.id", ondelete="CASCADE"))
    
    gross_premium = Column(Numeric(15, 2), nullable=False)
    ceded_premium = Column(Numeric(15, 2), nullable=False)
    reinsurance_commission = Column(Numeric(15, 2), default=0.00)
    net_to_reinsurer = Column(Numeric(15, 2), nullable=False) # ceded_premium - commission
    
    cession_date = Column(Date, default=date.today)
    
    status = Column(String(50), default='recorded') # 'recorded', 'paid'
    
    created_at = Column(DateTime, default=utcnow)

class ReinsuranceRecovery(Base):
    """
    Records the claim portion recoverable from a reinsurer.
    """
    __tablename__ = "reinsurance_recoveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"))
    treaty_id = Column(UUID(as_uuid=True), ForeignKey("reinsurance_treaties.id", ondelete="CASCADE"))
    
    gross_claim_amount = Column(Numeric(15, 2), nullable=False)
    recoverable_amount = Column(Numeric(15, 2), nullable=False)
    
    recovery_date = Column(Date, default=date.today)
    
    status = Column(String(50), default='pending') # 'pending', 'collected'
    
    created_at = Column(DateTime, default=utcnow)
