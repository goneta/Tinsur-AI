from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.rbac import Role, Permission
from app.services.security_service import SecurityService

class PermissionBase(BaseModel):
    id: str
    scope: str
    action: str
    description: str | None = None
    key: str

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    id: str
    name: str
    description: str | None = None
    permissions: List[PermissionBase] = []

    class Config:
        from_attributes = True

class AssignPermissionsRequest(BaseModel):
    permission_ids: List[str]

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/roles", response_model=List[RoleBase])
def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "read")
    return db.query(Role).all()

@router.get("/permissions", response_model=List[PermissionBase])
def list_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "read")
    return db.query(Permission).all()

@router.post("/roles/{role_id}/permissions")
def assign_permissions_to_role(
    role_id: str,
    request: AssignPermissionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    security = SecurityService(db)
    security.enforce_permission(current_user, "admin", "write")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Clear existing permissions? Or just add?
    # Usually "assign" means "set to this set"
    role.permissions = []
    
    for pid in request.permission_ids:
        perm = db.query(Permission).filter(Permission.id == pid).first()
        if perm:
            role.permissions.append(perm)
            
    db.commit()
    db.refresh(role)
    return {"status": "success", "role": role.name, "permission_count": len(role.permissions)}

# Helper to verify setup (dev only)
@router.post("/init-rbac")
def init_rbac(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only super admin can run this
    if current_user.role != "super_admin":
         raise HTTPException(status_code=403, detail="Only super_admin can init RBAC")

    # Create basic permissions
    perms = [
        ("admin", "read"), ("admin", "write"),
        ("policy", "read"), ("policy", "write"), ("policy", "create"),
        ("claim", "read"), ("claim", "write"),
        ("quote", "read"), ("quote", "write")
    ]
    
    for scope, action in perms:
        if not db.query(Permission).filter_by(scope=scope, action=action).first():
            db.add(Permission(scope=scope, action=action, description=f"Can {action} {scope}"))
            
    # Create basic roles
    roles = ["company_admin", "agent", "client", "manager"]
    for r_name in roles:
        if not db.query(Role).filter_by(name=r_name).first():
            db.add(Role(name=r_name, description=f"Role for {r_name}"))
            
    db.commit()
    return {"status": "RBAC initialized"}
