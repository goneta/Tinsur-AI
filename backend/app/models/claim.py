"""
Claim model for insurance claims.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Date, Numeric, Text
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from app.core.time import utcnow

from app.core.database import Base


class Claim(Base):
    """Claim model for insurance claims."""
    __tablename__ = "claims"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    claim_number = Column(String(50), unique=True, nullable=False)
    
    # Relationships
    policy_id = Column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    adjuster_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    
    # Incident Details
    incident_date = Column(Date, nullable=False)
    incident_description = Column(Text, nullable=False)
    incident_location = Column(String(255))
    
    # Status & Workflow
    status = Column(String(50), default='submitted')  # submitted, under_review, approved, rejected, paid, closed
    
    # Financials
    claim_amount = Column(Numeric(15, 2), nullable=False)  # Amount requested
    approved_amount = Column(Numeric(15, 2), nullable=True)  # Amount approved for payout
    
    # Documents
    evidence_files = Column(JSON, default=[])  # List of file URLs
    ai_assessment = Column(JSON, nullable=True) # AI-generated severity and estimates
    
    # Fraud Detection
    fraud_score = Column(Float, default=0.0) # Risk score (0.0 to 1.0)
    fraud_details = Column(JSON, default={}) # Specific fraud markers/reports
    evidence_hashes = Column(JSON, default=[]) # List of image fingerprints/hashes
    
    # Audit
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    policy = relationship("Policy", back_populates="claims")
    client = relationship("Client")
    company = relationship("Company")
    adjuster = relationship("User", foreign_keys=[adjuster_id])
    creator = relationship("User", foreign_keys=[created_by])
    activities = relationship("ClaimActivity", back_populates="claim", cascade="all, delete-orphan")
    product_claim_detail = relationship("ProductClaimDetail", back_populates="claim", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Claim {self.claim_number}>"
