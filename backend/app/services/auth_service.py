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
from fastapi import HTTPException, status


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, request: RegisterRequest) -> User:
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
        if request.company_name and request.company_subdomain:
            # Check if subdomain is available
            existing_company = self.db.query(Company).filter(
                Company.subdomain == request.company_subdomain
            ).first()
            if existing_company:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company subdomain already taken"
                )
            
            # Create new company
            company = Company(
                name=request.company_name,
                subdomain=request.company_subdomain,
                email=request.email
            )
            self.db.add(company)
            self.db.flush()
            company_id = company.id
            user_role = "company_admin"
        else:
            # User must be assigned to existing company by admin
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company information required for registration"
            )
        
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
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, request: LoginRequest) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.db.query(User).filter(User.email == request.email).first()
        
        if not user:
            return None
        
        if not verify_password(request.password, user.password_hash):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "company_id": str(user.company_id)
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
        user = self.authenticate_user(request)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        tokens = self.create_tokens(user)
        
        return {
            **tokens.dict(),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "company_id": str(user.company_id)
            }
        }
