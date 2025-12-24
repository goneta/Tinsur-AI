
from pydantic import BaseModel, Field
from typing import Optional, List

class LoyaltyRequest(BaseModel):
    client_id: str = Field(..., description="ID of the client")
    action: str = Field("view", description="Action (view, redeem)")

class LoyaltyResponse(BaseModel):
    points: int
    tier: str
    message: str
