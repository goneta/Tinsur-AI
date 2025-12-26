"""
Recovery models for Subrogation and Salvage.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class ClaimRecovery(Base):
    """
    Tracks efforts to recover claim payouts via Subrogation or Salvage.
    """
    __tablename__ = "claim_recoveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    
    # Type & Status
    recovery_type = Column(String(50), nullable=False) # 'subrogation', 'salvage'
    status = Column(String(50), default='identified') # 'identified', 'in_progress', 'negotiation', 'recovered', 'unrecoverable'
    
    # Financials
    estimated_amount = Column(Numeric(15, 2), default=0)
    actual_recovered_amount = Column(Numeric(15, 2), default=0)
    recovery_costs = Column(Numeric(15, 2), default=0) # Fees, towing, legal costs
    
    # Details
    third_party_info = Column(JSON, default={}) # Name, insurer, contact of at-fault party
    asset_details = Column(JSON, default={}) # For salvage: vehicle VIN, part details, auction info
    
    notes = Column(Text)
    
    # Audit
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    claim = relationship("Claim")
    assignee = relationship("User", foreign_keys=[assigned_to_id])
