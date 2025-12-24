from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class CommissionBase(BaseModel):
    agent_id: UUID
    policy_id: UUID
    amount: Decimal
    status: str = "pending"


class CommissionCreate(CommissionBase):
    pass


class CommissionUpdate(BaseModel):
    status: Optional[str] = None
    paid_at: Optional[datetime] = None


class CommissionSchema(CommissionBase):
    id: UUID
    company_id: UUID
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
