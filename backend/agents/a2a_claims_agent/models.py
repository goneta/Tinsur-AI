
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ClaimRequest(BaseModel):
    policy_id: Optional[str] = Field(None, description="ID of the policy associated with the claim")
    description: Optional[str] = Field(None, description="Description of the incident")
    amount: Optional[float] = Field(None, description="Estimated cost of the claim")
    incident_date: Optional[str] = Field(None, description="Date of the incident (YYYY-MM-DD)")

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    fraud_score: int
    message: str
    processed_at: str
