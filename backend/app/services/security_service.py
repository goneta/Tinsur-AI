"""
Security Service for RBAC Permission Checks.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.rbac import Role, Permission, role_permissions

class SecurityService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get a list of all permission keys (scope:action) for a user.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.role:
            return []

        # Find role by name (since User.role is currently a string)
        # TODO: Migration to make User.role a FK to roles table is planned but not yet active
        # For now, we look up the Role object by name
        
        # If the user role string matches a Role.name in DB
        role = self.db.query(Role).filter(Role.name == user.role).first()
        if not role:
            # Fallback for super_admin if not in DB, give all permissions? 
            # Or just return empty. Better to return empty for security.
            return []
            
        return [p.key for p in role.permissions]

    def check_permission(self, user: User, scope: str, action: str) -> bool:
        """
        Check if user has permission for specific action on scope.
        """
        if not user:
            return False
            
        # Optimization: cache permissions in request state if possible, but for now query DB
        perms = self.get_user_permissions(str(user.id))
        
        required_perm = f"{scope}:{action}"
        
        # Handle wildcards if we implement them later, e.g. "policy:*"
        # For now, exact match
        if required_perm in perms:
            return True
            
        # Super admin override check (optional, but good for bootstrapping)
        if user.role == "super_admin":
             return True
             
        return False

    def enforce_permission(self, user: User, scope: str, action: str):
        """
        Raise 403 if permission denied.
        """
        if not self.check_permission(user, scope, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Required {scope}:{action}"
            )
