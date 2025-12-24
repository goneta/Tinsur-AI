"""
Policy model for insurance policies.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Boolean, Integer, JSON, Numeric, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Policy(Base):
    """Policy model for active insurance policies."""
    __tablename__ = "policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    policy_type_id = Column(UUID(as_uuid=True), ForeignKey("policy_types.id"))
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=True)
    pos_location_id = Column(UUID(as_uuid=True), ForeignKey("pos_locations.id"), nullable=True)
    
    policy_number = Column(String(50), unique=True, nullable=False)
    sale_channel = Column(String(50), default='online')  # 'online', 'pos', 'agent', 'broker'
    
    # Coverage
    coverage_amount = Column(Numeric(15, 2))
    premium_amount = Column(Numeric(15, 2), nullable=False)
    premium_frequency = Column(String(50), default='annual')
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    status = Column(String(50), default='active')  # 'active', 'expired', 'canceled', 'lapsed'
    cancellation_reason = Column(Text)
    
    # Documents
    policy_document_url = Column(String(500))
    qr_code_data = Column(Text)
    
    # Additional data
    details = Column(JSON, default={})
    notes = Column(Text)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sales_agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    policy_type = relationship("PolicyType", back_populates="policies")
    quote = relationship("Quote", back_populates="policy")
    pos_location = relationship("POSLocation", back_populates="policies")
    creator = relationship("User", foreign_keys=[created_by])
    sales_agent = relationship("User", foreign_keys=[sales_agent_id])
    endorsements = relationship("Endorsement", back_populates="policy", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="policy", cascade="all, delete-orphan")
    co_insurance_shares = relationship("CoInsuranceShare", back_populates="policy", cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<Policy {self.policy_number}>"
    
    @property
    def is_active(self):
        """Check if policy is currently active."""
        today = datetime.now().date()
        return (
            self.status == 'active' and
            self.start_date <= today <= self.end_date
        )
    
    @property
    def days_until_expiry(self):
        """Calculate days until policy expires."""
        if self.end_date:
            return (self.end_date - datetime.now().date()).days
        return None

    @property
    def client_name(self):
        """Get client display name."""
        return self.client.display_name if self.client else "Unknown"

    @property
    def created_by_name(self):
        """Get creator name."""
        if self.creator and self.creator.role == 'client':
            return "Online"
        return self.creator.full_name if self.creator else "Unknown"
