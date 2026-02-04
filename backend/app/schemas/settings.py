"""
Pydantic schemas for user settings.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserSettingsBase(BaseModel):
    """Base schema for user settings."""
    theme: str = Field(default="light", pattern="^(light|dark)$")
    language: str = Field(default="en", pattern="^(en|fr|es)$")
    timezone: str = Field(default="UTC", max_length=50)
    date_format: str = Field(default="MM/DD/YYYY", max_length=50)
    currency_format: str = Field(default="USD", max_length=10)


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating user settings."""
    user_id: UUID


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")
    language: Optional[str] = Field(None, pattern="^(en|fr|es)$")
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=50)
    currency_format: Optional[str] = Field(None, max_length=10)


class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
