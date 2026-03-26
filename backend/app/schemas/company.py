"""
Pydantic schemas for Company settings.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class BankDetails(BaseModel):
    """Bank account details schema."""
    id: Optional[str] = None
    bank_name: str = Field(..., min_length=1, max_length=255)
    account_number: str = Field(..., min_length=1, max_length=100)
    account_name: str = Field(..., min_length=1, max_length=255)
    swift_code: Optional[str] = Field(None, max_length=50)
    branch: Optional[str] = Field(None, max_length=255)


class MobileMoneyAccount(BaseModel):
    """Mobile money account details schema."""
    id: Optional[str] = None
    provider: str = Field(..., min_length=1, max_length=100)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_name: str = Field(..., min_length=1, max_length=255)


class CompanyResponse(BaseModel):
    """Company response schema."""
    id: UUID
    name: str
    subdomain: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    registration_number: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    bank_details: List[BankDetails] = []
    mobile_money_accounts: List[MobileMoneyAccount] = []
    apr_percent: Optional[float] = 0.0
    arrangement_fee: Optional[float] = 0.0
    extra_fee: Optional[float] = 0.0
    # Mandatory Fees
    government_tax_percent: Optional[float] = 0.0
    admin_fee: Optional[float] = 0.0
    admin_fee_percent: Optional[float] = 0.0
    admin_discount_percent: Optional[float] = 0.0
    
    currency: str = "USD"
    country: Optional[str] = None
    timezone: str = "UTC"
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CompanyUpdate(BaseModel):
    """Schema for updating company information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    registration_number: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    bank_details: Optional[List[BankDetails]] = None
    mobile_money_accounts: Optional[List[MobileMoneyAccount]] = None
    apr_percent: Optional[float] = None
    arrangement_fee: Optional[float] = None
    extra_fee: Optional[float] = None
    # Mandatory Fees
    government_tax_percent: Optional[float] = None
    admin_fee: Optional[float] = None
    admin_fee_percent: Optional[float] = None
    admin_discount_percent: Optional[float] = None

    primary_color: Optional[str] = Field(None, max_length=10)
    secondary_color: Optional[str] = Field(None, max_length=10)
    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""
    name: str = Field(..., min_length=1, max_length=255)
    subdomain: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    registration_number: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="USD", max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    
    # Financial defaults
    apr_percent: float = 0.0
    arrangement_fee: float = 0.0
    extra_fee: float = 0.0
    government_tax_percent: float = 0.0
    admin_fee_percent: float = 0.0
    admin_discount_percent: float = 0.0
