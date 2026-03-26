
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TicketRequest(BaseModel):
    category: str = Field(..., description="Category of the ticket (e.g., policy, claim, technical)")
    priority: str = Field("medium", description="Priority level (low, medium, high, urgent)")
    subject: str = Field(..., description="Short summary of the issue")
    description: str = Field(..., description="Detailed description of the problem")
    client_id: Optional[str] = Field(None, description="ID of the client associated with the ticket")

class TicketResponse(BaseModel):
    ticket_number: str
    status: str
    message: str
    created_at: str
