"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import TokenData

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    token_data = TokenData(
        user_id=uuid.UUID(user_id),
        email=payload.get("email"),
        role=payload.get("role"),
        company_id=uuid.UUID(payload.get("company_id")) if payload.get("company_id") else None
    )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    return current_user


def require_role(allowed_roles: list[str]):
    """Dependency to check if user has required role."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker


# Pre-defined role dependencies
require_admin = require_role(["super_admin", "company_admin"])
require_manager = require_role(["super_admin", "company_admin", "manager"])
require_agent = require_role(["super_admin", "company_admin", "manager", "agent"])


async def get_current_client(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the client associated with the current user."""
    from app.models.client import Client
    
    # Check if user is linked to a client
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any client profile"
        )
        
    return client
