from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class MLModelBase(BaseModel):
    model_name: str
    model_type: str
    model_version: str
    accuracy: Optional[Decimal] = None
    is_active: bool = True

class MLModelCreate(MLModelBase):
    pass

class MLModelUpdate(BaseModel):
    is_active: Optional[bool] = None
    accuracy: Optional[Decimal] = None

class MLModel(MLModelBase):
    id: UUID
    deployed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
