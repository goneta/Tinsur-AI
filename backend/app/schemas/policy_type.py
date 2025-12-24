"""
Pydantic schemas for policy types.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class PolicyTypeBase(BaseModel):
    """Base schema for policy type."""
    name: str  # e.g., "Vehicle Insurance"
    code: str  # e.g., "AUTO"
    description: Optional[str] = None
    is_active: bool = True


class PolicyTypeCreate(PolicyTypeBase):
    """Schema for creating a policy type."""
    pass


class PolicyTypeUpdate(BaseModel):
    """Schema for updating a policy type."""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PolicyTypeResponse(PolicyTypeBase):
    """Schema for policy type response."""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PolicyTypeListResponse(BaseModel):
    """Schema for policy type list response."""
    policy_types: List[PolicyTypeResponse]
    total: int
    page: int = 1
    page_size: int = 50
