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

    async def register_or_login_google(self, request: GoogleLoginRequest) -> dict:
        """
        Process Google login. If user doesn't exist, create one based on user_type.
        """
        payload = await self.verify_google_token(request.token)
        email = payload["email"]
        
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Automated registration logic
            first_name = payload.get("first_name", "Google")
            last_name = payload.get("last_name", "User")
            
            company_id = None
            user_role = "client"
            
            if request.user_type == "company":
                # Create a minimal company for this google user
                # Ensure subdomain is unique
                base_subdomain = f"corp-{uuid.uuid4().hex[:8]}"
                subdomain = base_subdomain
                
                # Double check subdomain uniqueness
                existing_company = self.db.query(Company).filter(Company.subdomain == subdomain).first()
                if existing_company:
                    subdomain = f"corp-{uuid.uuid4().hex[:12]}"

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
                is_verified=True, # Social accounts are pre-verified
                password_hash=get_password_hash(uuid.uuid4().hex), # Random password for social users
                profile_picture=payload.get("picture")
            )
            self.db.add(user)
            self.db.flush() # Flush to get user ID for client creation
            print(f"DEBUG: Automatically registered new {user_role}: {email}")

        # IDEMPOTENCY: If it's a client but missing a Client profile, create it now
        if user.role == "client":
            client = self.db.query(Client).filter(Client.user_id == user.id).first()
            if not client:
                try:
                    # Default company: Thunderfam Group LTD
                    default_company_id = uuid.UUID("325d944d-1dc2-4541-9a77-835763b58f98")
                    
                    client_data = ClientCreate(
                        first_name=user.first_name or payload.get("first_name", "Google"),
                        last_name=user.last_name or payload.get("last_name", "User"),
                        email=email,
                        client_type="individual",
                        status="active",
                        company_id=default_company_id
                    )
                    # This will also trigger _create_automatic_driver (and linkage) inside ClientService
                    await self.client_service.create_client(client_data, user_id=user.id)
                    print(f"DEBUG: Provisioned Missing Client and Driver for existing google user: {email}")
                except Exception as e:
                    print(f"ERROR: Failed to provision Missing Client/Driver for google user {email}: {str(e)}")
                    # We don't want to fail the whole login if just the driver card fails
        
        # Standard login flow once user exists and is provisioned
        self.db.commit()
        
        return self.auth_service.login_manual_inject(user)

# Add a helper to AuthService to handle the response dictionary construction without re-authenticating
# Since I'm in dedicated service mode, I'll just copy the logic or extend AuthService locally.
