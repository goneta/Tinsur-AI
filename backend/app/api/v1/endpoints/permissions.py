
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.rbac import Role, Permission
from app.schemas.rbac import PermissionSchema, RoleSchema, RoleCreate, RoleUpdate

router = APIRouter()

@router.get("/permissions", response_model=List[PermissionSchema])
def list_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """List all available permissions."""
    return db.query(Permission).all()

@router.get("/roles", response_model=List[RoleSchema])
def list_roles(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """List all roles and their permissions."""
    return db.query(Role).all()

@router.get("/roles/{role_id}", response_model=RoleSchema)
def get_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get specific role details."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("/roles", response_model=RoleSchema)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Create a new role."""
    # Check uniqueness
    existing = db.query(Role).filter(Role.name == role_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    role = Role(name=role_in.name, description=role_in.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    
    # Assign permissions
    if role_in.permissions:
        perms = db.query(Permission).filter(Permission.id.in_(role_in.permissions)).all()
        role.permissions = perms
        db.commit()
        db.refresh(role)
        
    return role

@router.put("/roles/{role_id}", response_model=RoleSchema)
def update_role(
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update a role (description and permissions)."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    if role_in.description is not None:
        role.description = role_in.description
        
    if role_in.permissions is not None:
        perms = db.query(Permission).filter(Permission.id.in_(role_in.permissions)).all()
        role.permissions = perms
        
    db.commit()
    db.refresh(role)
    return role
