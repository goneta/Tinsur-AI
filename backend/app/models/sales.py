"""
Sales tracking models.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, Time, Integer
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from app.core.time import utcnow

from app.core.database import Base


class SalesTransaction(Base):
    """Sales transaction for policy sales."""
    __tablename__ = "sales_transactions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    policy_id = Column(GUID(), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    pos_location_id = Column(GUID(), ForeignKey("pos_locations.id"), nullable=True)

    channel = Column(String(50), nullable=False)  # pos, online, agent, mobile, partner
    sale_amount = Column(Numeric(15, 2), nullable=False)
    commission_amount = Column(Numeric(15, 2))
    sale_date = Column(Date, nullable=False)
    sale_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company")
    policy = relationship("Policy")
    employee = relationship("User", foreign_keys=[employee_id])
    pos_location = relationship("POSLocation")


class SalesTarget(Base):
    """Sales targets for employees."""
    __tablename__ = "sales_targets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    period = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    target_amount = Column(Numeric(15, 2))
    target_count = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=utcnow)

    employee = relationship("User", foreign_keys=[employee_id])
