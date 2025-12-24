
from pydantic import BaseModel
from typing import List, Optional
import uuid

class PermissionBase(BaseModel):
    scope: str
    action: str
    description: Optional[str] = None

class PermissionSchema(PermissionBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permissions: List[uuid.UUID] = []

class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[uuid.UUID]] = None

class RoleSchema(RoleBase):
    id: uuid.UUID
    permissions: List[PermissionSchema] = []
    class Config:
        from_attributes = True
