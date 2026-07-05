"""
Loyalty model for tracking client points.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.core.guid import GUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class LoyaltyPoint(Base):
    """Loyalty points model."""
    __tablename__ = "loyalty_points"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"))
    
    points_earned = Column(Integer, default=0)
    points_redeemed = Column(Integer, default=0)
    points_balance = Column(Integer, default=0)
    
    tier = Column(String(50), default='bronze') # 'bronze', 'silver', 'gold', 'platinum'
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    
    def __repr__(self):
        return f"<LoyaltyPoint Client-{self.client_id} {self.points_balance}>"
