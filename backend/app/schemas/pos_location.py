from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class POSLocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    manager_id: Optional[UUID] = None
    is_active: bool = True


class POSLocationCreate(POSLocationBase):
    pass


class POSLocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    manager_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class POSLocation(POSLocationBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
