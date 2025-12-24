from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class TicketBase(BaseModel):
    subject: str
    description: Optional[str] = None
    category: str
    priority: str = "medium"

class TicketCreate(TicketBase):
    client_id: Optional[UUID] = None

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    sla_breach_at: Optional[datetime] = None

class Ticket(TicketBase):
    id: UUID
    ticket_number: str
    company_id: UUID
    client_id: Optional[UUID]
    status: str
    assigned_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
