"""
Pydantic schemas for quotes.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class QuoteBase(BaseModel):
    """Base schema for quote."""
    client_id: UUID
    policy_type_id: UUID
    coverage_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    discount_percent: Decimal = Field(default=0, ge=0, le=100, decimal_places=2)
    tax_percent: Decimal = Field(default=0, ge=0, le=100, decimal_places=2)
    premium_frequency: str = Field(default='annual', pattern='^(monthly|quarterly|semi-annual|annual)$')
    duration_months: int = Field(default=12, ge=1, le=120)
    details: Optional[Dict[str, Any]] = {}
    notes: Optional[str] = None


class QuoteCalculationRequest(BaseModel):
    """Schema for quote calculation request (AI-powered)."""
    client_id: UUID
    policy_type_id: UUID
    coverage_amount: Decimal = Field(..., ge=0, decimal_places=2)
    premium_frequency: str = Field(default='annual')
    duration_months: int = Field(default=12, ge=1)
    
    # Risk factors (varies by policy type)
    risk_factors: Dict[str, Any] = Field(default_factory=dict)
    
    # Selected additional services
    selected_services: Optional[List[UUID]] = Field(default_factory=list)

    financial_overrides: Optional[Dict[str, Any]] = Field(default=None)
    # Overrides for base rate, fees, etc.


class QuoteCreate(QuoteBase):
    """Schema for creating a quote."""
    # Backend calculates premiums and validity
    created_by: Optional[UUID] = None
    pos_location_id: Optional[UUID] = None
    financial_overrides: Optional[Dict[str, Any]] = None
    selected_services: Optional[List[UUID]] = Field(default_factory=list)


class QuoteUpdate(BaseModel):
    """Schema for updating a quote."""
    coverage_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    premium_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    final_premium: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    premium_frequency: Optional[str] = None
    duration_months: Optional[int] = Field(None, ge=1, le=120)
    risk_score: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    status: Optional[str] = Field(None, pattern='^(draft|sent|accepted|rejected|expired)$')
    details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class QuoteResponse(QuoteBase):
    """Schema for quote response."""
    id: UUID
    company_id: UUID
    quote_number: str
    premium_amount: Decimal
    tax_percent: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    final_premium: Decimal
    apr_percent: Optional[float] = 0.0
    arrangement_fee: Optional[Decimal] = 0.0
    extra_fee: Optional[Decimal] = 0.0
    total_financed_amount: Optional[Decimal] = 0.0
    monthly_installment: Optional[Decimal] = 0.0
    total_installment_price: Optional[Decimal] = 0.0
    excess: Optional[Decimal] = 0.0
    included_services: Optional[List[str]] = []
    risk_score: Optional[Decimal]
    status: str
    valid_until: Optional[date] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    is_expired: bool
    client_name: str
    created_by_name: str
    policy_type_name: str
    
    class Config:
        from_attributes = True


class QuoteListResponse(BaseModel):
    """Schema for quote list response."""
    quotes: List[QuoteResponse]
    total: int
    page: int = 1
    page_size: int = 50


class QuoteCalculationResponse(BaseModel):
    """Schema for quote calculation response."""
    final_premium: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    base_premium: Decimal
    apr_percent: float
    arrangement_fee: Decimal
    extra_fee: Decimal
    total_financed_amount: Decimal
    monthly_installment: Decimal
    total_installment_price: Decimal
    excess: Decimal
    included_services: List[str]
    risk_score: Decimal
    risk_factors_analysis: Dict[str, Any]
    recommendations: Optional[List[str]] = []


class QuoteToPolicyConversion(BaseModel):
    """Schema for converting quote to policy."""
    start_date: date
    payment_method: str = Field(..., pattern='^(stripe|mobile_money|bank_transfer|cash)$')
    initial_payment_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
