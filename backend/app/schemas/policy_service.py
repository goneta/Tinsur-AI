from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

# Shared properties
class PolicyServiceBase(BaseModel):
    name_en: str
    name_fr: Optional[str] = None
    description: Optional[str] = None
    default_price: Decimal = Decimal("0.00")
    is_active: bool = True

# Properties to receive on creation
class PolicyServiceCreate(PolicyServiceBase):
    company_id: UUID

# Properties to receive on update
class PolicyServiceUpdate(PolicyServiceBase):
    name_en: Optional[str] = None
    company_id: Optional[UUID] = None

# Properties shared by models stored in DB
class PolicyServiceInDBBase(PolicyServiceBase):
    id: UUID
    company_id: UUID
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class PolicyService(PolicyServiceInDBBase):
    pass

# Properties stored in DB
class PolicyServiceInDB(PolicyServiceInDBBase):
    pass
