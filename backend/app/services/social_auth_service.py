"""
Social authentication service for handling Google login and automatic provisioning.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.client import Client
from app.models.company import Company
from app.services.auth_service import AuthService
from app.services.client_service import ClientService
from app.schemas.auth import GoogleLoginRequest, Token
from app.schemas.client import ClientCreate
from app.core.security import get_password_hash
import uuid
import string
import random

from app.core.config import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class SocialAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)
        self.client_service = ClientService(db)

    async def verify_google_token(self, token: str) -> dict:
        """
        Verify Google Token (ID Token or Access Token).
        Falls back to mock verification if GOOGLE_CLIENT_ID is not configured.
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

        if not settings.GOOGLE_CLIENT_ID:
            print("WARNING: GOOGLE_CLIENT_ID not configured. Using MOCK verification.")
            return self.verify_google_token_mock(token)

        # Check if it looks like a JWT (ID Token)
        if token.count('.') == 2:
            try:
                # Verify as ID token
                idinfo = id_token.verify_oauth2_token(
                    token, 
                    google_requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )

                return {
                    "sub": idinfo['sub'],
                    "email": idinfo['email'],
                    "first_name": idinfo.get('given_name', 'Google'),
                    "last_name": idinfo.get('family_name', 'User'),
                    "picture": idinfo.get('picture')
                }
            except Exception as e:
                print(f"Google ID Token Verification Error: {str(e)}")
                # Fall through to try as access_token
        
        # Try as Access Token by calling Google userinfo endpoint
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to verify Google access token"
                    )
                
                userinfo = response.json()
                return {
                    "sub": userinfo['sub'],
                    "email": userinfo['email'],
                    "first_name": userinfo.get('given_name', 'Google'),
                    "last_name": userinfo.get('family_name', 'User'),
                    "picture": userinfo.get('picture')
                }
        except Exception as e:
            print(f"Google Access Token Verification Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )

    def verify_google_token_mock(self, token: str) -> dict:
        """
        Legacy mock verification for development.
        """
        email = token if "@" in token else f"{token}@example.com"
        
        return {
            "sub": f"google_{token}",
            "email": email,
            "first_name": "Google",
            "last_name": "User",
            "picture": None
        }

    async def verify_facebook_token(self, token: str) -> dict:
        """
        Verify Facebook Access Token by calling the Graph API.
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Facebook token"
            )

        import httpx
        try:
            async with httpx.AsyncClient() as client:
                # Call Facebook Graph API to get user info
                # fields typically needed: id, email, first_name, last_name, name, picture
                response = await client.get(
                    "https://graph.facebook.com/v18.0/me",
                    params={
                        "fields": "id,name,email,first_name,last_name,picture",
                        "access_token": token
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    fb_error = response.json().get('error', {}).get('message', 'Failed to verify Facebook token')
                    print(f"Facebook Graph API Error: {fb_error}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Facebook verification failed: {fb_error}"
                    )
                
                fb_data = response.json()
                # Facebook picture is nested: picture.data.url
                picture_url = fb_data.get('picture', {}).get('data', {}).get('url')
                
                return {
                    "sub": f"facebook_{fb_data['id']}",
                    "email": fb_data.get('email'), # Note: Email might be null if not shared
                    "first_name": fb_data.get('first_name') or fb_data.get('name', 'Facebook'),
                    "last_name": fb_data.get('last_name') or '',
                    "picture": picture_url
                }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Facebook Access Token Verification Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )

    async def register_or_login_google(self, request: GoogleLoginRequest) -> dict:
        """
        Process Google login.
        """
        payload = await self.verify_google_token(request.token)
        return await self._process_social_login(payload, request.user_type, "Google")

    async def register_or_login_facebook(self, request: FacebookLoginRequest) -> dict:
        """
        Process Facebook login.
        """
        payload = await self.verify_facebook_token(request.token)
        return await self._process_social_login(payload, request.user_type, "Facebook")

    async def _process_social_login(self, payload: dict, user_type: str, provider_name: str) -> dict:
        """
        Generic logic for social login/registration.
        """
        email = payload.get("email")
        if not email:
            # If email is not available from social provider (common on Facebook if not requested/provided)
            # We use a fallback based on sub ID for tracking
            email = f"{payload['sub']}@social.tinsur.ai"

        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Automated registration logic
            first_name = payload.get("first_name", provider_name)
            last_name = payload.get("last_name", "User")
            
            company_id = None
            user_role = "client"
            
            if user_type == "company":
                # Create a minimal company for this social user
                base_subdomain = f"corp-{uuid.uuid4().hex[:8]}"
                subdomain = base_subdomain
                
                random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
                system_reg_num = f"COMP-{random_chars}"
                
                company = Company(
                    name=f"{first_name}'s Company",
                    subdomain=subdomain,
                    email=email,
                    system_registration_number=system_reg_num,
                    is_active=True
                )
                self.db.add(company)
                self.db.flush()
                company_id = company.id
                user_role = "company_admin"
            
            # Create the user
            user = User(
                company_id=company_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=user_role,
                is_active=True,
                is_verified=True,
                password_hash=get_password_hash(uuid.uuid4().hex),
                profile_picture=payload.get("picture")
            )
            self.db.add(user)
            self.db.flush()
            print(f"DEBUG: Automatically registered new {user_role}: {email} via {provider_name}")

        # IDEMPOTENCY: If it's a client but missing a Client profile, create it now
        if user.role == "client":
            client = self.db.query(Client).filter(Client.user_id == user.id).first()
            if not client:
                try:
                    # Default company: Thunderfam Group LTD
                    default_company_id = uuid.UUID("325d944d-1dc2-4541-9a77-835763b58f98")
                    
                    client_data = ClientCreate(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=email,
                        client_type="individual",
                        status="active",
                        company_id=default_company_id
                    )
                    await self.client_service.create_client(client_data, user_id=user.id)
                    print(f"DEBUG: Provisioned Missing Client and Driver for existing social user: {email}")
                except Exception as e:
                    print(f"ERROR: Failed to provision Missing Client/Driver for social user {email}: {str(e)}")
        
        self.db.commit()
        return self.auth_service.login_manual_inject(user)

# Add a helper to AuthService to handle the response dictionary construction without re-authenticating
# Since I'm in dedicated service mode, I'll just copy the logic or extend AuthService locally.
