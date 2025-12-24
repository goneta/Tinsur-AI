"""
Pydantic schemas for payments.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class PaymentMethodBase(BaseModel):
    """Base schema for payment method details."""
    method: str = Field(..., pattern='^(stripe|mobile_money|bank_transfer|cash)$')
    gateway: Optional[str] = None  # 'stripe', 'orange_money', 'mtn_money', 'moov_money', 'wave'


class StripePaymentMethod(PaymentMethodBase):
    """Schema for Stripe payment."""
    method: str = Field(default='stripe', pattern='stripe')
    gateway: str = Field(default='stripe')
    payment_intent_id: Optional[str] = None
    customer_id: Optional[str] = None


class MobileMoneyPaymentMethod(PaymentMethodBase):
    """Schema for Mobile Money payment."""
    method: str = Field(default='mobile_money', pattern='mobile_money')
    gateway: str = Field(..., pattern='^(orange_money|mtn_money|moov_money|wave)$')
    phone_number: str = Field(..., min_length=10, max_length=15)
    operator_transaction_id: Optional[str] = None


class BankTransferPaymentMethod(PaymentMethodBase):
    """Schema for Bank Transfer payment."""
    method: str = Field(default='bank_transfer', pattern='bank_transfer')
    bank_name: str
    account_number: str
    reference_number: Optional[str] = None


class PaymentBase(BaseModel):
    """Base schema for payment."""
    policy_id: UUID
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default='XOF', max_length=3)


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    payment_method: str = Field(..., pattern='^(stripe|mobile_money|bank_transfer|cash)$')
    payment_gateway: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""
    status: Optional[str] = Field(None, pattern='^(pending|processing|completed|failed|refunded)$')
    reference_number: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: UUID
    company_id: UUID
    client_id: UUID
    payment_number: str
    payment_method: str
    payment_gateway: Optional[str]
    status: str
    reference_number: Optional[str]
    payment_metadata: Dict[str, Any]
    failure_reason: Optional[str]
    paid_at: Optional[datetime]
    refunded_at: Optional[datetime]
    client_name: Optional[str] = None
    policy_number_display: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """Schema for payment list response."""
    payments: List[PaymentResponse]
    total: int
    page: int = 1
    page_size: int = 50


class PaymentProcessRequest(BaseModel):
    """Schema for processing a payment."""
    policy_id: UUID
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    payment_details: Dict[str, Any]  # Contains method-specific details


class PaymentRefundRequest(BaseModel):
    """Schema for payment refund."""
    refund_amount: Decimal = Field(..., ge=0, decimal_places=2)
    reason: str = Field(..., min_length=10)


class WebhookPayload(BaseModel):
    """Schema for payment webhook payload."""
    event_type: str
    gateway: str
    transaction_id: str
    status: str
    amount: Decimal
    metadata: Optional[Dict[str, Any]] = {}


class PaymentReceiptResponse(BaseModel):
    """Schema for payment receipt."""
    payment_number: str
    client_name: str
    policy_number: str
    amount: Decimal
    currency: str
    payment_method: str
    payment_date: datetime
    reference_number: Optional[str]
    receipt_url: Optional[str]
