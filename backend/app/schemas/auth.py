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

    @classmethod
    def sanitize_email(cls, v: str) -> str:
        return v.lower().strip() if v else v

    from pydantic import field_validator
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return cls.sanitize_email(v)


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[str] = None


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    company_name: Optional[str] = None  # For creating new company
    company_subdomain: Optional[str] = None
    rccm_number: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    """Google login/register request schema."""
    token: str
    user_type: str # 'client' or 'company'
class FacebookLoginRequest(BaseModel):
    """Facebook login/register request schema."""
    token: str
    user_type: str # 'client' or 'company'
