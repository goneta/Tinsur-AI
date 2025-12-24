from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import random
import string

from app.core import dependencies as deps
from app.models.ticket import Ticket
from app.schemas import ticket as schemas

router = APIRouter()

def generate_ticket_number():
    return f"TKT-{random.randint(10000, 99999)}"

@router.post("/", response_model=schemas.Ticket)
def create_ticket(
    *,
    db: Session = Depends(deps.get_db),
    ticket_in: schemas.TicketCreate,
    current_user = Depends(deps.get_current_active_user),
):
    """
    Create a new support ticket.
    """
    ticket = Ticket(
        company_id=current_user.company_id,
        client_id=ticket_in.client_id,
        ticket_number=generate_ticket_number(),
        category=ticket_in.category,
        priority=ticket_in.priority,
        subject=ticket_in.subject,
        description=ticket_in.description,
        assigned_to=current_user.id # Auto-assign creator for now, or null
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/", response_model=List[schemas.Ticket])
def read_tickets(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve tickets.
    """
    tickets = db.query(Ticket).filter(
        Ticket.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    return tickets
