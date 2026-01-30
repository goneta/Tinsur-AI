"""
Social authentication router.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import GoogleLoginRequest, FacebookLoginRequest
from app.services.social_auth_service import SocialAuthService

router = APIRouter()

@router.post("/google", response_model=dict)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with Google ID token. 
    If user doesn't exist, they are registered based on user_type.
    """
    social_service = SocialAuthService(db)
    return await social_service.register_or_login_google(request)

@router.post("/facebook", response_model=dict)
async def facebook_login(
    request: FacebookLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with Facebook Access Token. 
    If user doesn't exist, they are registered based on user_type.
    """
    social_service = SocialAuthService(db)
    return await social_service.register_or_login_facebook(request)
