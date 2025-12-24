"""
POS Inventory model for tracking physical materials at POS locations.
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class POSInventory(Base):
    """POS Inventory model."""
    __tablename__ = "pos_inventory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pos_location_id = Column(UUID(as_uuid=True), ForeignKey("pos_locations.id", ondelete="CASCADE"))
    
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pos_location = relationship("POSLocation", back_populates="inventory")
    transactions = relationship("POSInventoryTransaction", back_populates="inventory_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<POSInventory {self.item_name} at {self.pos_location_id}>"


class POSInventoryTransaction(Base):
    """Transaction history for POS Inventory items."""
    __tablename__ = "pos_inventory_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("pos_inventory.id", ondelete="CASCADE"))
    
    quantity_change = Column(Integer, nullable=False) # Negative for deduction, Positive for addition
    transaction_type = Column(String(50), nullable=False) # 'sale', 'restock', 'adjustment', 'return'
    reference_id = Column(UUID(as_uuid=True), nullable=True) # e.g. Policy ID, or Restock Order ID
    
    notes = Column(String(500))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_item = relationship("POSInventory", back_populates="transactions")
    creator = relationship("User")
