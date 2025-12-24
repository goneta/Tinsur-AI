
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class CoInsuranceShare(Base):
    """Model for sharing policy risk between insurance companies."""
    __tablename__ = "co_insurance_shares"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    share_percentage = Column(Numeric(5, 2), nullable=False) # e.g. 30.00%
    fee_percentage = Column(Numeric(5, 2), default=0) # Management fee paid to lead insurer
    
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    policy = relationship("Policy", back_populates="co_insurance_shares")
    company = relationship("Company")

    def __repr__(self):
        return f"<CoInsuranceShare {self.company_id}: {self.share_percentage}%>"
