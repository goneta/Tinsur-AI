"""
API endpoints for policy types.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.policy_type import PolicyType
from app.schemas.policy_type import (
    PolicyTypeCreate,
    PolicyTypeUpdate,
    PolicyTypeResponse,
    PolicyTypeListResponse
)
from app.repositories.policy_type_repository import PolicyTypeRepository

router = APIRouter()


@router.post("/", response_model=PolicyTypeResponse, status_code=status.HTTP_201_CREATED)
def create_policy_type(
    type_data: PolicyTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new policy type."""
    repo = PolicyTypeRepository(db)
    
    # Check if code exists
    existing = repo.get_by_code(current_user.company_id, type_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy type with this code already exists"
        )
    
    policy_type = PolicyType(
        company_id=current_user.company_id,
        **type_data.model_dump()
    )
    
    return repo.create(policy_type)


@router.get("/", response_model=PolicyTypeListResponse)
def list_policy_types(
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List policy types."""
    repo = PolicyTypeRepository(db)
    
    skip = (page - 1) * page_size
    types, total = repo.get_by_company(
        company_id=current_user.company_id,
        skip=skip,
        limit=page_size,
        is_active=is_active
    )
    
    return {
        "policy_types": types,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{type_id}", response_model=PolicyTypeResponse)
def get_policy_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a policy type by ID."""
    repo = PolicyTypeRepository(db)
    
    policy_type = repo.get_by_id(type_id)
    if not policy_type or policy_type.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy type not found"
        )
    
    return policy_type


@router.put("/{type_id}", response_model=PolicyTypeResponse)
def update_policy_type(
    type_id: UUID,
    type_data: PolicyTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a policy type."""
    repo = PolicyTypeRepository(db)
    
    policy_type = repo.get_by_id(type_id)
    if not policy_type or policy_type.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy type not found"
        )
    
    # Update fields
    for field, value in type_data.model_dump(exclude_unset=True).items():
        setattr(policy_type, field, value)
    
    return repo.update(policy_type)


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a policy type."""
    repo = PolicyTypeRepository(db)
    
    policy_type = repo.get_by_id(type_id)
    if not policy_type or policy_type.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy type not found"
        )
    
    repo.delete(type_id)
    return None
