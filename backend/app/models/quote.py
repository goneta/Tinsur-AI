"""
Quote model for insurance quotes.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Numeric, Date, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta

from app.core.database import Base


class Quote(Base):
    """Quote model for insurance quotes."""
    __tablename__ = "quotes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    policy_type_id = Column(UUID(as_uuid=True), ForeignKey("policy_types.id"))
    pos_location_id = Column(UUID(as_uuid=True), ForeignKey("pos_locations.id"), nullable=True)
    quote_number = Column(String(50), unique=True, nullable=False)
    sale_channel = Column(String(50), default='online')  # 'online', 'pos', 'agent', 'broker'
    
    # Amounts
    coverage_amount = Column(Numeric(15, 2))
    premium_amount = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    final_premium = Column(Numeric(15, 2), nullable=False)
    
    # Configuration
    premium_frequency = Column(String(50), default='annual')  # 'monthly', 'quarterly', 'annual'
    duration_months = Column(Integer, default=12)
    risk_score = Column(Numeric(5, 2))
    
    # Status
    status = Column(String(50), default='draft')  # 'draft', 'sent', 'accepted', 'rejected', 'expired'
    valid_until = Column(Date)
    
    # Additional data
    details = Column(JSON, default={})
    notes = Column(Text)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    policy_type = relationship("PolicyType", back_populates="quotes")
    creator = relationship("User", foreign_keys=[created_by])
    pos_location = relationship("POSLocation")
    policy = relationship("Policy", back_populates="quote", uselist=False)
    
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
