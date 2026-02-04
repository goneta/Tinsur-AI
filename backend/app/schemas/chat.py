"""
Chat schemas for internal communication.
"""
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ChatChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_private: bool = False


class ChatChannelCreate(ChatChannelBase):
    company_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    member_ids: Optional[List[UUID]] = None


class ChatChannelResponse(ChatChannelBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatChannelMemberResponse(BaseModel):
    id: UUID
    channel_id: UUID
    user_id: UUID
    added_by: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatMessageBase(BaseModel):
    channel_id: UUID
    message: str = Field(..., min_length=1)
    attachments: Optional[List[Any]] = None


class ChatMessageCreate(ChatMessageBase):
    company_id: Optional[UUID] = None
    sender_id: Optional[UUID] = None


class ChatMessageResponse(ChatMessageBase):
    id: UUID
    company_id: UUID
    sender_id: UUID
    read_by: List[Any] = []
    reactions: List[Any] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
