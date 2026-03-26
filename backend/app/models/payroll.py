"""
Payroll Transaction model for tracking employee payments.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class PayrollTransaction(Base):
    """
    Payroll Transaction model.
    Records payments made to employees.
    """
    __tablename__ = "payroll_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    # Payment Details
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='XOF')
    payment_date = Column(DateTime, default=utcnow)
    payment_month = Column(String(20)) # e.g., "2024-12" or "December 2024"
    
    payment_method = Column(String(50)) # 'mobile_money', 'bank_transfer'
    
    # Itemized Breakdown
    base_salary = Column(Numeric(15, 2), default=0)
    transport_allowance = Column(Numeric(15, 2), default=0)
    housing_allowance = Column(Numeric(15, 2), default=0)
    commissions_total = Column(Numeric(15, 2), default=0)
    
    # Deductions
    tax_is = Column(Numeric(15, 2), default=0) # Impôt sur le Salaire
    tax_cn = Column(Numeric(15, 2), default=0) # Contribution Nationale
    tax_igr = Column(Numeric(15, 2), default=0) # Impôt Général sur le Revenu
    social_security_cnps = Column(Numeric(15, 2), default=0) # CNPS
    
    net_pay = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default='pending') # 'pending', 'paid', 'failed'
    
    # Metadata
    description = Column(String(255)) # e.g., "Salary December 2024"
    reference_number = Column(String(100)) # External transaction ID
    failure_reason = Column(Text)
    
    # Audit
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    employee = relationship("User", foreign_keys=[employee_id], backref="payroll_received")
    company = relationship("Company", backref="payrolls")
    processor = relationship("User", foreign_keys=[processed_by])

    def __repr__(self):
        return f"<PayrollTransaction {self.id} - {self.status}>"
