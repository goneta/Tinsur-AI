
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReferralRequest(BaseModel):
    client_id: str = Field(..., description="ID of the client making the referral")
    referred_email: str = Field(..., description="Email of the referred person")
    referred_name: str = Field(..., description="Name of the referred person")

class ReferralResponse(BaseModel):
    referral_code: str
    message: str
