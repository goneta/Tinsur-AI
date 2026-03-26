from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class LoyaltyPointBase(BaseModel):
    points_balance: int = 0
    tier: str = "bronze"

class LoyaltyPointCreate(BaseModel):
    client_id: UUID
    points_earned: int = 0

class LoyaltyPointUpdate(BaseModel):
    points_earned: Optional[int] = None
    points_redeemed: Optional[int] = None
    tier: Optional[str] = None

class LoyaltyPoint(LoyaltyPointBase):
    id: UUID
    client_id: UUID
    points_earned: int
    points_redeemed: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
