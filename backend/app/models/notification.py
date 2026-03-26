"""
Notification model for tracking sent notifications.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base


class Notification(Base):
    """Notification model for tracking all sent notifications."""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    # Recipients
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    
    # Notification details
    notification_type = Column(String(50), nullable=False)  # 'payment_reminder', 'policy_renewal', 'quote_sent', 'payment_received', etc.
    channel = Column(String(50), nullable=False)  # 'email', 'sms', 'whatsapp', 'push'
    
    # Recipient information
    recipient_email = Column(String(255))
    recipient_phone = Column(String(50))
    
    # Content
    subject = Column(String(500))
    content = Column(Text, nullable=False)
    template_id = Column(String(100))
    
    # Status
    status = Column(String(50), default='pending')  # 'pending', 'sent', 'delivered', 'failed', 'bounced'
    
    # Delivery tracking
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # Gateway response
    external_id = Column(String(200))  # ID from email/SMS service
    gateway_response = Column(JSON, default={})
    
    # Optional metadata for linking/debugging
    notification_metadata = Column(JSON, default={})  # Additional context (policy_id, payment_id, etc.)
    
    # Retry
    retry_count = Column(String(10), default='0')
    max_retries = Column(String(10), default='3')
    
    # Audit
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    user = relationship("User")
    client = relationship("Client")
    
    def __repr__(self):
        return f"<Notification {self.notification_type} via {self.channel} - {self.status}>"
