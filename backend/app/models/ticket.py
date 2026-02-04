"""
Ticket model for support system.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.schema import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class Ticket(Base):
    """Support ticket model."""
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    
    ticket_number = Column(String(50), unique=True, nullable=False)
    category = Column(String(100)) 
    priority = Column(String(50), default='medium')
    status = Column(String(50), default='open')
    
    subject = Column(String(255), nullable=False)
    description = Column(Text)
    
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    resolved_at = Column(DateTime, nullable=True)
    sla_breach_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    assigned_user = relationship("User")
    
    def __repr__(self):
        return f"<Ticket {self.ticket_number}>"

class TicketMessage(Base):
    """Message within a support ticket thread."""
    __tablename__ = "ticket_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"))
    sender_id = Column(UUID(as_uuid=True), nullable=True) 
    
    sender_type = Column(String(20), default='user') 
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False) 
    
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    ticket = relationship("Ticket", backref="messages")
