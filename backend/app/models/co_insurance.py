
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, Text
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class CoInsuranceShare(Base):
    """Model for sharing policy risk between insurance companies."""
    __tablename__ = "co_insurance_shares"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    policy_id = Column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    share_percentage = Column(Numeric(5, 2), nullable=False) # e.g. 30.00%
    fee_percentage = Column(Numeric(5, 2), default=0) # Management fee paid to lead insurer
    
    created_at = Column(DateTime, default=utcnow)
    notes = Column(Text)
    
    # Relationships
    policy = relationship("Policy", back_populates="co_insurance_shares")
    company = relationship("Company")

    def __repr__(self):
        return f"<CoInsuranceShare {self.company_id}: {self.share_percentage}%>"
