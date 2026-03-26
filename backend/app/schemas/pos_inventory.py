from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class POSInventoryBase(BaseModel):
    item_name: str
    quantity: int = 0
    low_stock_threshold: int = 10


class POSInventoryCreate(POSInventoryBase):
    pos_location_id: UUID


class POSInventoryUpdate(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None


class POSInventory(POSInventoryBase):
    id: UUID
    pos_location_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
