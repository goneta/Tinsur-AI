
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

class PolicyCreationRequest(BaseModel):
    quote_id: Optional[str] = Field(None, description="ID of the accepted quote")
    start_date: Optional[str] = Field(None, description="Desired start date (YYYY-MM-DD)")
    customer_id: Optional[str] = Field(None, description="Customer ID if known")

class PolicyResponse(BaseModel):
    policy_id: str
    status: str
    effective_date: str
    expiry_date: str
    message: str
