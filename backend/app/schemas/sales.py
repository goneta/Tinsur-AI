"""
Sales schemas.
"""
from datetime import date, datetime, time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class SalesTransactionBase(BaseModel):
    policy_id: UUID
    employee_id: Optional[UUID] = None
    pos_location_id: Optional[UUID] = None
    channel: str = Field(..., pattern="^(pos|online|agent|mobile|partner)$")
    sale_amount: float
    commission_amount: Optional[float] = None
    sale_date: date
    sale_time: time


class SalesTransactionCreate(SalesTransactionBase):
    company_id: Optional[UUID] = None


class SalesTransactionResponse(SalesTransactionBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SalesTargetBase(BaseModel):
    employee_id: UUID
    period: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    target_amount: Optional[float] = None
    target_count: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class SalesTargetCreate(SalesTargetBase):
    pass


class SalesTargetResponse(SalesTargetBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
