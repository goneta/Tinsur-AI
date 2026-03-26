from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

class ShareCodeBase(BaseModel):
    share_type: str
    recipient_ids: List[str] # IDs as strings to be flexible (User or Client UUIDs)

class ShareCodeCreate(ShareCodeBase):
    pass

class ShareCodeUpdate(BaseModel):
    status: Optional[str] = None
    recipient_ids: Optional[List[str]] = None

class ShareCodeInDBBase(ShareCodeBase):
    id: UUID
    code: str
    creator_id: UUID
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ShareCode(ShareCodeInDBBase):
    qr_code_base64: Optional[str] = None # Helper field for API response

class ShareCodeValidate(BaseModel):
    code: str
