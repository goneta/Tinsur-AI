
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.ticket import Ticket
import uuid
from datetime import datetime

@tool
def create_support_ticket(client_id: str, company_id: str, subject: str, description: str, category: str = "general", priority: str = "medium") -> str:
    """
    Creates a new support ticket in the database.
    Args:
        client_id: The UUID of the client filing the ticket.
        company_id: The UUID of the company.
        subject: Brief title of the issue.
        description: Detailed explanation.
        category: 'technical', 'billing', 'claim', 'complaint', or 'general'.
        priority: 'low', 'medium', 'high', or 'urgent'.
    """
    db = SessionLocal()
    try:
        new_ticket = Ticket(
            company_id=uuid.UUID(company_id),
            client_id=uuid.UUID(client_id),
            ticket_number=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            category=category,
            priority=priority,
            subject=subject,
            description=description,
            status='open'
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        
        return f"Ticket created successfully! Number: {new_ticket.ticket_number}. We will get back to you soon."
    except Exception as e:
        db.rollback()
        return f"Error creating ticket: {str(e)}"
    finally:
        db.close()

@tool
def get_ticket_status(company_id: str, ticket_number: str) -> str:
    """
    Retrieves the status and details of a specific support ticket.
    Args:
        company_id: The UUID of the company.
        ticket_number: Examples: 'TKT-A1B2C3D4'
    """
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(
            Ticket.company_id == uuid.UUID(company_id),
            Ticket.ticket_number == ticket_number.upper()
        ).first()
        if not ticket:
            return f"Ticket {ticket_number} not found in company {company_id}."
            
        return (f"Ticket {ticket.ticket_number}:\n"
                f"- Subject: {ticket.subject}\n"
                f"- Status: {ticket.status}\n"
                f"- Priority: {ticket.priority}\n"
                f"- Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        return f"Error retrieving ticket status: {str(e)}"
    finally:
        db.close()

@tool
def list_active_tickets(company_id: str, client_id: str) -> str:
    """
    Lists all active (non-closed) support tickets for a specific client.
    Args:
        company_id: The UUID of the company.
        client_id: The UUID of the client.
    """
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).filter(
            Ticket.company_id == uuid.UUID(company_id),
            Ticket.client_id == uuid.UUID(client_id),
            Ticket.status != 'closed'
        ).all()
        
        if not tickets:
            return "You have no active support tickets in this company."
            
        lines = [f"- {t.ticket_number}: {t.subject} ({t.status})" for t in tickets]
        return "Active Tickets:\n" + "\n".join(lines)
    except Exception as e:
        return f"Error listing tickets: {str(e)}"
    finally:
        db.close()
