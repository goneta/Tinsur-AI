"""
POS Location model for physical points of sale.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class POSLocation(Base):
    """POS Location model."""
    __tablename__ = "pos_locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    region = Column(String(100))
    
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    manager = relationship("User", foreign_keys=[manager_id])
    employees = relationship("User", back_populates="pos_location", foreign_keys="User.pos_location_id")
    policies = relationship("Policy", back_populates="pos_location")
    inventory = relationship("POSInventory", back_populates="pos_location", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<POSLocation {self.name}>"
