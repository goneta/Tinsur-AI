from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class PremiumPolicyCriteriaBase(BaseModel):
    name: str
    description: Optional[str] = None
    field_name: str
    operator: str
    value: str

class PremiumPolicyCriteriaCreate(PremiumPolicyCriteriaBase):
    pass

class PremiumPolicyCriteriaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    field_name: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None

class PremiumPolicyCriteriaResponse(PremiumPolicyCriteriaBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PremiumPolicyTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    is_active: bool = True

class PremiumPolicyTypeCreate(PremiumPolicyTypeBase):
    criteria_ids: List[UUID] = []

class PremiumPolicyTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None
    criteria_ids: Optional[List[UUID]] = None

class PremiumPolicyTypeResponse(PremiumPolicyTypeBase):
    id: UUID
    company_id: UUID
    criteria: List[PremiumPolicyCriteriaResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PremiumPolicyTypeListResponse(BaseModel):
    premium_policy_types: List[PremiumPolicyTypeResponse]
    total: int
    page: int
    page_size: int
