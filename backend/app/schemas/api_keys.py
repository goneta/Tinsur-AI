"""
Pydantic schemas for API Key management.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ApiKeyBase(BaseModel):
    name: str
    agent_id: Optional[str] = None
    expires_at: Optional[datetime] = None

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    agent_id: Optional[str] = None

class ApiKeyResponse(ApiKeyBase):
    id: UUID
    key_prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ApiKeyCreatedResponse(ApiKeyResponse):
    plain_text_key: str  # Only returned once on creation
