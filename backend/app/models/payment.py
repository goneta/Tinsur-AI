"""
Payment and PaymentTransaction models for payment processing.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Text, Numeric
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Text, Numeric
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base


class Payment(Base):
    """Payment model for tracking policy payments."""
    __tablename__ = "payments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"))
    policy_id = Column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"))
    client_id = Column(GUID(), ForeignKey("clients.id", ondelete="CASCADE"))
    
    # Payment details
    payment_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='XOF')  # West African CFA Franc
    
    # Payment method
    payment_method = Column(String(50), nullable=False)  # 'stripe', 'mobile_money', 'bank_transfer', 'cash'
    payment_gateway = Column(String(50))  # 'stripe', 'orange_money', 'mtn_money', 'moov_money', 'wave'
    
    # Status
    status = Column(String(50), default='pending')  # 'pending', 'processing', 'completed', 'failed', 'refunded'
    
    # Metadata
    reference_number = Column(String(100))  # External reference from payment gateway
    payment_metadata = Column(JSON, default={})
    failure_reason = Column(Text)
    
    # Timestamps
    paid_at = Column(DateTime)
    refunded_at = Column(DateTime)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    company = relationship("Company")
    policy = relationship("Policy")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by])
    transactions = relationship("PaymentTransaction", back_populates="payment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Payment {self.payment_number} - {self.status}>"

    @property
    def client_name(self):
        if self.client:
            return self.client.display_name
        return None

    @property
    def policy_number_display(self):
        if self.policy:
            return self.policy.policy_number
        return None

    @property
    def premium_frequency(self):
        if self.policy:
            return self.policy.premium_frequency
        return None

    @property
    def created_by_name(self):
        if self.creator:
            if hasattr(self.creator, 'role') and self.creator.role == 'client':
                return "Online"
            return f"{self.creator.first_name} {self.creator.last_name}"
        return "Online"


class PaymentTransaction(Base):
    """Payment Transaction model for detailed transaction logs."""
    __tablename__ = "payment_transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    payment_id = Column(GUID(), ForeignKey("payments.id", ondelete="CASCADE"))
    
    # Transaction details
    transaction_id = Column(String(200), unique=True)  # Gateway transaction ID
    gateway = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='XOF')
    
    # Status
    status = Column(String(50), nullable=False)  # 'initiated', 'pending', 'success', 'failed'
    
    # Gateway response
    gateway_response = Column(JSON, default={})
    error_code = Column(String(100))
    error_message = Column(Text)
    
    # Timestamps
    initiated_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    payment = relationship("Payment", back_populates="transactions")
    
    def __repr__(self):
        return f"<PaymentTransaction {self.transaction_id} - {self.status}>"
