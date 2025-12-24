
from pydantic import BaseModel, Field
from typing import Optional, List

class TelematicsRequest(BaseModel):
    policy_id: str = Field(..., description="Policy ID")
    period: str = Field("last_30_days", description="Time period")

class TelematicsResponse(BaseModel):
    score: float
    distance: float
    message: str
