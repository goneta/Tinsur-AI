"""
User schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "agent"
    profile_picture: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str
    company_id: uuid.UUID
    created_by: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    """User update schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    pos_location_id: Optional[uuid.UUID] = None


class UserInDB(UserBase):
    """User in database schema."""
    id: uuid.UUID
    company_id: uuid.UUID
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    last_login: Optional[datetime] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    role: Optional[str] = None
    
    # Branding info from company
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    company_logo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User response schema."""
    pass
