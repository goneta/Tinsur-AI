"""
Loyalty model for tracking client points.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class LoyaltyPoint(Base):
    """Loyalty points model."""
    __tablename__ = "loyalty_points"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    
    points_earned = Column(Integer, default=0)
    points_redeemed = Column(Integer, default=0)
    points_balance = Column(Integer, default=0)
    
    tier = Column(String(50), default='bronze') # 'bronze', 'silver', 'gold', 'platinum'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client")
    
    def __repr__(self):
        return f"<LoyaltyPoint Client-{self.client_id} {self.points_balance}>"
