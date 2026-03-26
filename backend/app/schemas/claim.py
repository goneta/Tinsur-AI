"""
Pydantic schemas for claims.
"""
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from uuid import UUID

class ClaimBase(BaseModel):
    """Base schema for claim data."""
    policy_id: UUID
    incident_date: date
    incident_description: str
    incident_location: Optional[str] = None
    claim_amount: float = Field(..., gt=0)
    evidence_files: List[str] = []

class ClaimCreate(ClaimBase):
    """Schema for creating a new claim."""
    company_id: Optional[UUID] = None
    created_by: Optional[UUID] = None

class ClaimUpdate(BaseModel):
    """Schema for updating a claim."""
    status: Optional[str] = None
    approved_amount: Optional[float] = None
    adjuster_id: Optional[UUID] = None
    incident_description: Optional[str] = None
    evidence_files: Optional[List[str]] = None
    notes: Optional[str] = None

class ClaimResponse(ClaimBase):
    """Schema for claim response."""
    id: UUID
    claim_number: str
    company_id: UUID
    client_id: UUID
    status: str
    approved_amount: Optional[float] = None
    adjuster_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    ai_assessment: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
