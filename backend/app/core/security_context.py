"""
Security Service for RBAC enforcement.
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rbac import Role, Permission, role_permissions
from typing import List, Set
import uuid

class SecurityService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user_id: uuid.UUID) -> Set[str]:
        """
        Get all permissions for a user as a set of "scope:action" strings.
        Resolves via User -> Role -> Permissions.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return set()

        # If User.role is a string (legacy), we fetch the Role object by name
        # If User.role_id existed, we'd use that. 
        # For now, we assume User.role matches Role.name
        role_name = user.role
        role = self.db.query(Role).filter(Role.name == role_name).first()
        
        if not role:
             # Fallback: maybe default permissions for hardcoded roles if DB not seeded?
             # For now, return empty to be safe.
             return set()

        perms = set()
        for p in role.permissions:
            perms.add(p.key)
            
        return perms

    def has_permission(self, user_id: uuid.UUID, scope: str, action: str) -> bool:
        """
        Check if user has specific permission.
        """
        required_perm = f"{scope}:{action}"
        user_perms = self.get_user_permissions(user_id)
        
        # Super admin bypass?
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.role == "super_admin":
            return True

        return required_perm in user_perms
