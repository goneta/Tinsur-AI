"""
Quote Element model for configurable quote parameters.
"""
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Numeric, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime
from app.core.database import Base

class QuoteElement(Base):
    """
    Represents a configurable element for quote calculations.
    Categories:
    - base_rate: Percentage used as starting point (e.g. 5%)
    - coverage_amount: Insured value choices
    - risk_multiplier: Adjustment factors (e.g. 1.25x)
    - fixed_fee: Flat charges (e.g. 500)
    """
    __tablename__ = "quote_elements"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Category of the element
    category = Column(String(50), nullable=False) # 'base_rate', 'coverage_amount', 'risk_multiplier', 'fixed_fee'
    
    name = Column(String(100), nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company")

    def __repr__(self):
        return f"<QuoteElement {self.name} ({self.category})>"
