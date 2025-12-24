"""
Premium Schedule model for tracking payment schedules.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class PremiumSchedule(Base):
    """Premium Schedule model for payment schedules."""
    __tablename__ = "premium_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"))
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    
    # Schedule details
    installment_number = Column(String(50), nullable=False)  # e.g., "1 of 12"
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default='pending')  # 'pending', 'paid', 'overdue', 'waived'
    
    # Grace period
    grace_period_days = Column(Numeric(5, 0), default=15)
    grace_period_ends = Column(Date)
    
    # Late fees
    late_fee = Column(Numeric(15, 2), default=0)
    late_fee_applied = Column(Boolean, default=False)
    
    # Reminders
    reminder_sent_at = Column(DateTime)
    overdue_reminder_sent_at = Column(DateTime)
    
    # Payment details
    paid_at = Column(DateTime)
    paid_amount = Column(Numeric(15, 2))
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    policy = relationship("Policy")
    payment = relationship("Payment")
    
    def __repr__(self):
        return f"<PremiumSchedule {self.installment_number} - {self.status}>"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        if self.status == 'paid':
            return False
        today = datetime.now().date()
        grace_end = self.grace_period_ends or self.due_date
        return today > grace_end
