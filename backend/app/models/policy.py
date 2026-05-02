"""
Policy model for insurance policies.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Boolean, Integer, JSON, Numeric, Date, Text
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base
from app.models.regulatory import IFRS17Group
from app.models.policy_service import PolicyService


class Policy(Base):
    """Policy model for active insurance policies."""
    __tablename__ = "policies"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    policy_type_id = Column(GUID(), ForeignKey("premium_policy_types.id"))
    quote_id = Column(GUID(), ForeignKey("quotes.id"), nullable=True)
    pos_location_id = Column(GUID(), ForeignKey("pos_locations.id"), nullable=True)
    ifrs17_group_id = Column(GUID(), ForeignKey("ifrs17_groups.id"), nullable=True)
    
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    sale_channel = Column(String(50), default='online')  # 'online', 'pos', 'agent', 'broker'
    
    # Coverage
    coverage_amount = Column(Numeric(15, 2))
    premium_amount = Column(Numeric(15, 2), nullable=False)
    premium_frequency = Column(String(50), default='annual')
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    status = Column(String(50), default='active', index=True)  # 'pending_activation', 'active', 'suspended', 'cancelled', 'expired', 'renewed'
    cancellation_reason = Column(Text)
    auto_renew = Column(Boolean, default=False)
    
    # Documents
    policy_document_url = Column(String(500))
    qr_code_data = Column(Text)
    
    # Additional data
    details = Column(JSON, default={})
    notes = Column(Text)
    
    # Audit
    created_by = Column(GUID(), ForeignKey("users.id"))
    sales_agent_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    policy_type = relationship("PremiumPolicyType")
    quote = relationship("Quote", back_populates="policy")
    pos_location = relationship("POSLocation", back_populates="policies")
    ifrs17_group = relationship("IFRS17Group")
    creator = relationship("User", foreign_keys=[created_by])
    sales_agent = relationship("User", foreign_keys=[sales_agent_id])
    endorsements = relationship("Endorsement", back_populates="policy", cascade="all, delete-orphan")

    claims = relationship("Claim", back_populates="policy", cascade="all, delete-orphan")
    product_rating_snapshot = relationship("ProductRatingSnapshot", back_populates="policy", uselist=False, cascade="all, delete-orphan")
    co_insurance_shares = relationship("CoInsuranceShare", back_populates="policy", cascade="all, delete-orphan")
    
    # Services
    services = relationship(
        "PolicyService",
        secondary="policy_service_association",
        backref="policies",
        lazy="selectin"
    )

    
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
