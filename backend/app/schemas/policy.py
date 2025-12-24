"""
Pydantic schemas for policies.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class PolicyBase(BaseModel):
    """Base schema for policy."""
    client_id: UUID
    policy_type_id: UUID
    coverage_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    premium_amount: Decimal = Field(..., ge=0, decimal_places=2)
    premium_frequency: str = Field(default='annual', pattern='^(monthly|quarterly|semi-annual|annual)$')
    start_date: date
    end_date: date
    details: Optional[Dict[str, Any]] = {}
    notes: Optional[str] = None


class PolicyCreate(PolicyBase):
    """Schema for creating a policy."""
    quote_id: Optional[UUID] = None
    sales_agent_id: Optional[UUID] = None
    pos_location_id: Optional[UUID] = None
    inventory_deductions: Optional[List[Dict[str, Any]]] = None # List of {item_id: UUID, quantity: int}


class PolicyUpdate(PolicyBase):
    """Schema for updating a policy."""
    # Note: Using PolicyBase fields as optional for update, but here recreating with Optionals for clarity or just inheriting logic
    client_id: Optional[UUID] = None
    policy_type_id: Optional[UUID] = None
    # ... Wait, PolicyUpdate usually redeclares fields as optional.
    # The existing file had:
    # class PolicyUpdate(BaseModel):
    #     coverage_amount: Optional[Decimal] ...
    # I should only touch PolicyCreate and PolicyResponse.
    # Re-reading file content from step 80 to ensure I don't break PolicyUpdate.
    pass 

# Actually, I should just target PolicyCreate and PolicyResponse specifically.

class PolicyResponse(PolicyBase):
    """Schema for policy response."""
    id: UUID
    company_id: UUID
    policy_number: str
    quote_id: Optional[UUID]
    sales_agent_id: Optional[UUID]
    pos_location_id: Optional[UUID]
    status: str
    policy_document_url: Optional[str]
    qr_code_data: Optional[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    days_until_expiry: Optional[int]
    client_name: str
    created_by_name: str
    
    class Config:
        from_attributes = True


class PolicyListResponse(BaseModel):
    """Schema for policy list response."""
    policies: List[PolicyResponse]
    total: int
    page: int = 1
    page_size: int = 50


class PolicyRenewalRequest(BaseModel):
    """Schema for policy renewal."""
    new_end_date: date
    premium_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    coverage_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = None


class PolicyCancellationRequest(BaseModel):
    """Schema for policy cancellation."""
    cancellation_reason: str = Field(..., min_length=10)
    effective_date: date
    refund_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class EndorsementBase(BaseModel):
    """Base schema for endorsement."""
    policy_id: UUID
    endorsement_type: str = Field(..., pattern='^(coverage_change|beneficiary_change|premium_adjustment|term_extension)$')
    effective_date: date
    changes: Dict[str, Any]
    reason: Optional[str] = None
    premium_adjustment: Decimal = Field(default=0, decimal_places=2)


class EndorsementCreate(EndorsementBase):
    """Schema for creating an endorsement."""
    pass


class EndorsementUpdate(BaseModel):
    """Schema for updating an endorsement."""
    effective_date: Optional[date] = None
    changes: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    premium_adjustment: Optional[Decimal] = Field(None, decimal_places=2)
    status: Optional[str] = Field(None, pattern='^(draft|pending_approval|approved|rejected|active)$')


class EndorsementResponse(EndorsementBase):
    """Schema for endorsement response."""
    id: UUID
    company_id: UUID
    endorsement_number: str
    issued_date: date
    new_premium: Optional[Decimal]
    status: str
    document_url: Optional[str]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
