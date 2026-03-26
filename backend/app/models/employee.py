"""
Employee Profile model for extended user information related to HR and Payroll.
"""
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
import uuid

from app.core.database import Base

class EmployeeProfile(Base):
    """
    Employee Profile model.
    Extends the User model with HR and Payroll specific details.
    """
    __tablename__ = "employee_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Payment preferences
    payment_method = Column(String(50)) # 'mobile_money', 'bank_transfer'
    
    # Mobile Money Details
    mobile_money_provider = Column(String(50)) # 'orange', 'mtn', 'wave', 'moov'
    mobile_money_number = Column(String(50))
    
    # Bank Details
    bank_name = Column(String(100))
    bank_account_number = Column(String(50))
    bank_account_holder_name = Column(String(100))
    iban = Column(String(50))
    swift_bic = Column(String(20))
    
    # Job Details
    job_title = Column(String(100))
    department = Column(String(100))
    base_salary = Column(Numeric(15, 2))
    currency = Column(String(3), default='XOF')

    # Relationships
    user = relationship("User", backref=backref("employee_profile", uselist=False))

    def __repr__(self):
        return f"<EmployeeProfile user_id={self.user_id}>"
