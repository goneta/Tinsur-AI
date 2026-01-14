from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

# Minimal Schema for embedded PolicyService response
class PolicyServiceRef(BaseModel):
    id: UUID
    name_en: str
    name_fr: Optional[str] = None
    default_price: Decimal
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

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
    excess: Decimal = Decimal("0.00")
    is_active: bool = True

class PremiumPolicyTypeCreate(PremiumPolicyTypeBase):
    criteria_ids: List[UUID] = []
    service_ids: List[UUID] = []

class PremiumPolicyTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    excess: Optional[Decimal] = None
    is_active: Optional[bool] = None
    criteria_ids: Optional[List[UUID]] = None
    service_ids: Optional[List[UUID]] = None

class PremiumPolicyTypeResponse(PremiumPolicyTypeBase):
    id: UUID
    company_id: UUID
    criteria: List[PremiumPolicyCriteriaResponse] = []
    services: List[PolicyServiceRef] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PremiumPolicyTypeListResponse(BaseModel):
    premium_policy_types: List[PremiumPolicyTypeResponse]
    total: int
    page: int
    page_size: int

class PremiumPolicyMatchResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: List[PremiumPolicyTypeResponse] = []
    recommended_id: Optional[UUID] = None
    missing_fields: List[str] = []

class PremiumPolicyMatchRequest(BaseModel):
    client_id: Optional[UUID] = None
    vehicle_details: Optional[dict] = None
    driver_details: Optional[dict] = None


