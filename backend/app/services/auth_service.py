"""
Authentication service for user registration and login.
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import uuid

from app.models.user import User
from app.models.company import Company
from app.schemas.auth import RegisterRequest, LoginRequest, Token
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.agent_client import AgentClient
from fastapi import HTTPException, status
import json


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, request: RegisterRequest) -> User:
        """Register a new user and optionally create a company."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # If company details provided, create new company
        company_id = None
        user_role = "client"  # Default role for self-registration
        
        if request.company_name and request.company_subdomain:
            # Company registration flow
            # Check if subdomain is available
            existing_company = self.db.query(Company).filter(
                Company.subdomain == request.company_subdomain
            ).first()
            if existing_company:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company subdomain already taken"
                )
            
            # Generate system registration number
            import string
            import random
            random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
            system_reg_num = f"COMP-{random_chars}"

            # Create new company
            company = Company(
                name=request.company_name,
                subdomain=request.company_subdomain,
                email=request.email,
                phone=request.phone,
                address=request.address,
                registration_number=request.rccm_number,  # Map RCCM to registration_number column
                system_registration_number=system_reg_num
            )
            self.db.add(company)
            self.db.flush()
            company_id = company.id
            user_role = "company_admin"
        else:
            # Client self-registration flow (no company required)
            company_id = None
            user_role = "client"
        
        # Create user
        user = User(
            company_id=company_id,
            email=request.email,
            password_hash=get_password_hash(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=user_role,
            is_verified=False  # Require email verification
        )

        # Compliance & AML Agent Screening
        try:
            agent_client = AgentClient()
            reg_details = {
                "first_name": request.first_name,
                "last_name": request.last_name,
                "email": request.email,
                "phone": request.phone,
                "role": user_role
            }
            
            # Call agent asynchronously
            response = await agent_client.send_message(
                "compliance_aml_agent", 
                json.dumps(reg_details),
                context={"company_id": str(company_id)}
            )
            
            if "messages" in response and response["messages"]:
                last_msg = response["messages"][-1]
                compliance_data = json.loads(last_msg["text"])
                
                user.compliance_status = compliance_data.get("status", "flagged")
                user.is_high_risk = compliance_data.get("is_high_risk", False)
                user.compliance_notes = compliance_data.get("notes", "No notes provided.")
                
                # If flagged or high risk, deactivate for manual review
                if user.compliance_status == "flagged" or user.is_high_risk:
                    user.is_active = False
                    print(f"User {request.email} FLAGGED for compliance review.")
        except Exception as e:
            print(f"Compliance Agent Error: {str(e)}")
            user.compliance_status = "error"
            user.compliance_notes = f"Failed to run compliance check: {str(e)}"
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, request: LoginRequest) -> Optional[User]:
        """Authenticate user with email and password."""
        print(f"DEBUG: Login attempt for {request.email}")
        user = self.db.query(User).filter(User.email == request.email).first()
        
        if not user:
            print("DEBUG: User not found")
            from fastapi import HTTPException
            raise HTTPException(401, detail=f"DEBUG: User {request.email} NOT found in DB")
            # return None
            
        print(f"DEBUG: User found {user.id}, verifying password...")
        is_valid = verify_password(request.password, user.password_hash)
        print(f"DEBUG: Password valid? {is_valid}")
        
        if not is_valid:
            from fastapi import HTTPException
            raise HTTPException(401, detail=f"DEBUG: Password mismatch for {request.email}. Hash starts: {user.password_hash[:10]}")
            # return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        # user.last_login = datetime.utcnow()
        # self.db.commit()
        
        return user
    
    def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "company_id": str(user.company_id) if user.company_id else None
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    def login(self, request: LoginRequest) -> dict:
        """Login and return tokens with user info."""
        # DEBUG WRAPPER
        print(f"DEBUG: Processing login for {request.email}")
        user = self.authenticate_user(request)
        
        if not user:
             # Should be caught by authenticate_user raising exception, but just in case
             raise HTTPException(status_code=401, detail="Authentication failed")
        
        print(f"DEBUG: Creating tokens for user {user.id}")
        tokens = self.create_tokens(user)
        print("DEBUG: Tokens created successfully")
        
        print("DEBUG: Constructing response dict")
        try:
            res = {
                **tokens.dict(),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "company_id": str(user.company_id) if user.company_id else None,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "mfa_enabled": user.mfa_enabled,
                    "created_at": user.created_at.isoformat() if (user.created_at and hasattr(user.created_at, 'isoformat')) else str(user.created_at) if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if (user.updated_at and hasattr(user.updated_at, 'isoformat')) else str(user.updated_at) if user.updated_at else None,
                    "profile_picture": user.profile_picture,
                    "pos_location_id": str(user.pos_location_id) if user.pos_location_id else None
                }
            }
            print("DEBUG: Response dict constructed")
            return res
        except Exception as e:
            print(f"DEBUG: Error in Constructing response dict: {str(e)}")
            raise e

    def login_manual_inject(self, user: User) -> dict:
        """Helper to create tokens and return standard response for a user already found/created."""
        tokens = self.create_tokens(user)
        return {
            **tokens.dict(),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "company_id": str(user.company_id) if user.company_id else None,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "mfa_enabled": user.mfa_enabled,
                "created_at": user.created_at.isoformat() if (user.created_at and hasattr(user.created_at, 'isoformat')) else str(user.created_at) if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if (user.updated_at and hasattr(user.updated_at, 'isoformat')) else str(user.updated_at) if user.updated_at else None,
                "profile_picture": user.profile_picture,
                "pos_location_id": str(user.pos_location_id) if user.pos_location_id else None
            }
        }
