"""
API endpoints for policy templates.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.policy_template import PolicyTemplate
from app.schemas.policy_template import (
    PolicyTemplateCreate,
    PolicyTemplateUpdate,
    PolicyTemplateResponse,
    PolicyTemplateListResponse
)
from app.repositories.policy_template_repository import PolicyTemplateRepository

router = APIRouter()


@router.post("/", response_model=PolicyTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_policy_template(
    template_data: PolicyTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new policy template."""
    repo = PolicyTemplateRepository(db)
    
    template = PolicyTemplate(
        company_id=current_user.company_id,
        **template_data.model_dump(),
        created_by=current_user.id
    )
    
    return repo.create(template)


@router.get("/", response_model=PolicyTemplateListResponse)
def list_policy_templates(
    policy_type_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    language: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List policy templates with filters."""
    repo = PolicyTemplateRepository(db)
    
    skip = (page - 1) * page_size
    templates, total = repo.get_by_company(
        company_id=current_user.company_id,
        policy_type_id=policy_type_id,
        is_active=is_active,
        language=language,
        skip=skip,
        limit=page_size
    )
    
    return {
        "templates": templates,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{template_id}", response_model=PolicyTemplateResponse)
def get_policy_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a policy template by ID."""
    repo = PolicyTemplateRepository(db)
    
    template = repo.get_by_id(template_id)
    if not template or template.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy template not found"
        )
    
    return template


@router.put("/{template_id}", response_model=PolicyTemplateResponse)
def update_policy_template(
    template_id: UUID,
    template_data: PolicyTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a policy template."""
    repo = PolicyTemplateRepository(db)
    
    template = repo.get_by_id(template_id)
    if not template or template.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy template not found"
        )
    
    # Update fields
    for field, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    
    return repo.update(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a policy template."""
    repo = PolicyTemplateRepository(db)
    
    template = repo.get_by_id(template_id)
    if not template or template.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy template not found"
        )
    
    repo.delete(template_id)
    return None
