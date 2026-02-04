from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class ReferralBase(BaseModel):
    referrer_client_id: UUID
    referred_client_id: Optional[UUID] = None
    reward_amount: Optional[Decimal] = None

class ReferralCreate(BaseModel):
    # Usually created by system or via a simple request to generate code
    referrer_client_id: Optional[UUID] = None # If admin creates it

class ReferralUpdate(BaseModel):
    status: Optional[str] = None
    reward_paid: Optional[bool] = None

class Referral(ReferralBase):
    id: UUID
    company_id: UUID
    referral_code: str
    status: str
    reward_paid: bool
    converted_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
