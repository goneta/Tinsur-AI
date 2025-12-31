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
    try:
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
    except (JWTError, ValidationError, ValueError):
        raise credentials_exception
    
    from sqlalchemy.orm import joinedload
    user = db.query(User).options(joinedload(User.company)).filter(User.id == token_data.user_id).first()
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


def require_permission(permission_code: str):
    """Dependency to check if user has a specific permission via RBAC."""
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 1. Super Admin bypass
        if current_user.role == "super_admin":
            return current_user
            
        # 2. Check Role in DB
        from app.models.rbac import Role
        # Check if user's role string maps to an RBAC Role
        role_record = db.query(Role).filter(Role.name == current_user.role).first()
        
        if not role_record:
            # Fallback: if role not in DB, deny or use legacy checks?
            # For now, deny strict permissions if RBAC is active
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role configuration not found for '{current_user.role}'"
            )
            
        # 3. Check Permissions
        has_perm = any(p.code == permission_code for p in role_record.permissions)
        if not has_perm:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_code}"
            )

        return current_user
    return permission_checker


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
