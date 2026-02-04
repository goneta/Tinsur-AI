"""
Claim activity schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ClaimActivityBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class ClaimActivityCreate(ClaimActivityBase):
    user_id: Optional[UUID] = None


class ClaimActivityResponse(ClaimActivityBase):
    id: UUID
    claim_id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
