"""
Quote model for insurance quotes.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Numeric, Date, Text, Integer
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Numeric, Date, Text, Integer
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime, timedelta
from app.core.time import utcnow

from app.core.database import Base


class Quote(Base):
    """Quote model for insurance quotes."""
    __tablename__ = "quotes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"))
    policy_type_id = Column(GUID(), ForeignKey("premium_policy_types.id"))
    pos_location_id = Column(GUID(), ForeignKey("pos_locations.id"), nullable=True)
    quote_number = Column(String(50), unique=True, nullable=False)
    sale_channel = Column(String(50), default='online')  # 'online', 'pos', 'agent', 'broker'
    
    # Amounts
    coverage_amount = Column(Numeric(15, 2))
    premium_amount = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    final_premium = Column(Numeric(15, 2), nullable=False)

    # Financial Snapshot (Calculated at creation)
    apr_percent = Column(Float, default=0.0)
    arrangement_fee = Column(Numeric(15, 2), default=0.0)
    admin_fee = Column(Numeric(15, 2), default=0.0) # Calculated amount
    admin_fee_percent = Column(Float, default=0.0) # Snapshot percent
    admin_discount_percent = Column(Float, default=0.0) # Snapshot percent
    extra_fee = Column(Numeric(15, 2), default=0.0)
    total_financed_amount = Column(Numeric(15, 2), default=0.0)
    monthly_installment = Column(Numeric(15, 2), default=0.0)
    total_installment_price = Column(Numeric(15, 2), default=0.0)
    
    # Calculation audit trail
    calculation_breakdown = Column(JSON, default={})
    
    # Premium Policy Snapshot
    excess = Column(Numeric(15, 2), default=0.0)
    included_services = Column(JSON, default=[])
    
    # Configuration
    premium_frequency = Column(String(50), default='annual')  # 'monthly', 'quarterly', 'annual'
    duration_months = Column(Integer, default=12)
    risk_score = Column(Numeric(5, 2))
    
    # Status
    status = Column(String(50), default='draft')  # 'draft', 'draft_from_client', 'sent', 'accepted', 'policy_created', 'submitted', 'under_review', 'approved', 'rejected', 'expired', 'archived'
    valid_until = Column(Date)
    valid_for_days = Column(Integer, default=30)
    
    # Additional data
    details = Column(JSON, default={})
    notes = Column(Text)
    
    # Audit
    created_by = Column(GUID(), ForeignKey("users.id"))
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    policy_type = relationship("PremiumPolicyType", foreign_keys=[policy_type_id])
    creator = relationship("User", foreign_keys=[created_by])
    pos_location = relationship("POSLocation")
    policy = relationship("Policy", back_populates="quote", uselist=False)
    underwriting_snapshot = relationship("QuoteUnderwritingSnapshot", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quote {self.quote_number}>"
    
    @property
    def is_expired(self):
        """Check if quote is expired."""
        if self.valid_until:
            return datetime.now().date() > self.valid_until
        return False
        
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

    @property
    def policy_type_name(self):
        """Get policy type name."""
        return self.policy_type.name if self.policy_type else "Unknown Policy"
