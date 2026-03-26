"""
Pydantic schemas for premium schedules.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class PremiumScheduleBase(BaseModel):
    """Base schema for premium schedule."""
    policy_id: UUID
    installment_number: str
    due_date: date
    amount: Decimal = Field(..., ge=0, multiple_of=Decimal('0.01'))
    grace_period_days: Decimal = Field(default=15, ge=0, le=90)


class PremiumScheduleCreate(PremiumScheduleBase):
    """Schema for creating a premium schedule."""
    pass


class PremiumScheduleUpdate(BaseModel):
    """Schema for updating a premium schedule."""
    status: Optional[str] = Field(None, pattern='^(pending|paid|overdue|waived)$')
    late_fee: Optional[Decimal] = Field(None, ge=0, multiple_of=Decimal('0.01'))
    paid_amount: Optional[Decimal] = Field(None, ge=0, multiple_of=Decimal('0.01'))


class PremiumScheduleResponse(PremiumScheduleBase):
    """Schema for premium schedule response."""
    id: UUID
    company_id: UUID
    payment_id: Optional[UUID]
    status: str
    grace_period_ends: Optional[date]
    late_fee: Decimal
    late_fee_applied: bool
    reminder_sent_at: Optional[datetime]
    overdue_reminder_sent_at: Optional[datetime]
    paid_at: Optional[datetime]
    paid_amount: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    is_overdue: bool
    model_config = ConfigDict(from_attributes=True)


class PremiumScheduleListResponse(BaseModel):
    """Schema for premium schedule list response."""
    schedules: List[PremiumScheduleResponse]
    total: int
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal


class PremiumCalculationRequest(BaseModel):
    """Schema for premium calculation."""
    total_premium: Decimal = Field(..., ge=0, multiple_of=Decimal('0.01'))
    frequency: str = Field(..., pattern='^(monthly|quarterly|semi-annual|annual)$')
    start_date: date
    duration_months: int = Field(..., ge=1, le=120)
    grace_period_days: int = Field(default=15, ge=0, le=90)


class PremiumCalculationResponse(BaseModel):
    """Schema for premium calculation response."""
    installments: List[Dict[str, Any]]
    total_installments: int
    installment_amount: Decimal
    total_amount: Decimal


class PaymentReminderRequest(BaseModel):
    """Schema for payment reminder."""
    schedule_id: UUID
    reminder_type: str = Field(..., pattern='^(upcoming|due_today|overdue)$')
    channels: List[str] = Field(default=['email'])  # 'email', 'sms', 'whatsapp'
