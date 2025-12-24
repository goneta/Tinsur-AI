"""
Repository for POS Inventory operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.pos_inventory import POSInventory, POSInventoryTransaction

class POSInventoryRepository:
    """Repository for POS Inventory."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, item_id: UUID) -> Optional[POSInventory]:
        """Get inventory item by ID."""
        return self.db.query(POSInventory).filter(POSInventory.id == item_id).first()
        
    def get_by_location(self, location_id: UUID) -> List[POSInventory]:
        """Get all inventory for a location."""
        return self.db.query(POSInventory).filter(POSInventory.pos_location_id == location_id).all()
        
    def create(self, item: POSInventory) -> POSInventory:
        """Create new inventory item."""
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
        
    def update(self, item: POSInventory) -> POSInventory:
        """Update inventory item."""
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
        
    def deduct_inventory(
        self, 
        item_id: UUID, 
        quantity: int, 
        transaction_type: str, 
        reference_id: Optional[UUID] = None,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> Optional[POSInventory]:
        """
        Deduct quantity from inventory and record transaction.
        Returns updated item or None if insufficient stock/error.
        """
        item = self.get_by_id(item_id)
        if not item:
            return None
            
        # Check sufficient stock for 'sale' type logic, 
        # though allow negative for corrections if needed? 
        # Strict for sales:
        if transaction_type == 'sale' and item.quantity < quantity:
            raise ValueError(f"Insufficient stock for {item.item_name}. Available: {item.quantity}, Requested: {quantity}")
            
        # Update quantity
        item.quantity -= quantity
        
        # Create transaction record
        transaction = POSInventoryTransaction(
            inventory_id=item_id,
            quantity_change=-quantity,
            transaction_type=transaction_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by
        )
        self.db.add(transaction)
        self.db.add(item)
        
        try:
            self.db.commit()
            self.db.refresh(item)
            return item
        except IntegrityError:
            self.db.rollback()
            return None
            
    def add_stock(
        self, 
        item_id: UUID, 
        quantity: int, 
        transaction_type: str = "restock", 
        reference_id: Optional[UUID] = None,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> Optional[POSInventory]:
        """Add stock to inventory."""
        item = self.get_by_id(item_id)
        if not item:
            return None
            
        item.quantity += quantity
        
        transaction = POSInventoryTransaction(
            inventory_id=item_id,
            quantity_change=quantity,
            transaction_type=transaction_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by
        )
        self.db.add(transaction)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
