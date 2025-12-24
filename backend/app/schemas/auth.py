"""
Authentication schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[uuid.UUID] = None


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None  # For creating new company
    company_subdomain: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str
