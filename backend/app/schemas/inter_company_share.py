from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class InterCompanyShareBase(BaseModel):
    to_company_id: UUID
    resource_type: str
    resource_id: UUID
    access_level: str = "read"
    expires_at: Optional[datetime] = None

class InterCompanyShareCreate(InterCompanyShareBase):
    pass

class InterCompanyShareUpdate(BaseModel):
    access_level: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_revoked: Optional[bool] = None

class InterCompanyShare(InterCompanyShareBase):
    id: UUID
    from_company_id: UUID
    from_company_name: Optional[str] = None
    to_company_name: Optional[str] = None
    is_revoked: bool
    created_at: datetime
    amount: Optional[float] = None
    currency: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
