from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.premium_policy import PremiumPolicyCriteria, PremiumPolicyType
from app.schemas.premium_policy import (
    PremiumPolicyCriteriaCreate,
    PremiumPolicyCriteriaUpdate,
    PremiumPolicyCriteriaResponse,
    PremiumPolicyTypeCreate,
    PremiumPolicyTypeUpdate,
    PremiumPolicyTypeResponse,
    PremiumPolicyTypeListResponse
)

router = APIRouter()

# --- Criteria Endpoints ---

@router.post("/criteria", response_model=PremiumPolicyCriteriaResponse, status_code=status.HTTP_201_CREATED)
def create_criteria(
    criteria_data: PremiumPolicyCriteriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new premium policy criteria."""
    criteria = PremiumPolicyCriteria(
        company_id=current_user.company_id,
        **criteria_data.model_dump()
    )
    db.add(criteria)
    db.commit()
    db.refresh(criteria)
    return criteria

@router.get("/criteria", response_model=List[PremiumPolicyCriteriaResponse])
def list_criteria(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available criteria for the company."""
    return db.query(PremiumPolicyCriteria).filter(
        PremiumPolicyCriteria.company_id == current_user.company_id
    ).all()

@router.put("/criteria/{criteria_id}", response_model=PremiumPolicyCriteriaResponse)
def update_criteria(
    criteria_id: UUID,
    criteria_data: PremiumPolicyCriteriaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a criteria."""
    criteria = db.query(PremiumPolicyCriteria).filter(
        PremiumPolicyCriteria.id == criteria_id,
        PremiumPolicyCriteria.company_id == current_user.company_id
    ).first()
    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")
    
    for field, value in criteria_data.model_dump(exclude_unset=True).items():
        setattr(criteria, field, value)
    
    db.commit()
    db.refresh(criteria)
    return criteria

@router.delete("/criteria/{criteria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_criteria(
    criteria_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a criteria."""
    criteria = db.query(PremiumPolicyCriteria).filter(
        PremiumPolicyCriteria.id == criteria_id,
        PremiumPolicyCriteria.company_id == current_user.company_id
    ).first()
    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")
    
    db.delete(criteria)
    db.commit()
    return None

# --- Policy Type Endpoints ---

@router.post("/types", response_model=PremiumPolicyTypeResponse, status_code=status.HTTP_201_CREATED)
def create_premium_policy_type(
    type_data: PremiumPolicyTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new premium policy type."""
    criteria_ids = type_data.criteria_ids
    type_dict = type_data.model_dump()
    del type_dict['criteria_ids']
    
    policy_type = PremiumPolicyType(
        company_id=current_user.company_id,
        **type_dict
    )
    
    if criteria_ids:
        criteria = db.query(PremiumPolicyCriteria).filter(
            PremiumPolicyCriteria.id.in_(criteria_ids),
            PremiumPolicyCriteria.company_id == current_user.company_id
        ).all()
        policy_type.criteria = criteria
        
    db.add(policy_type)
    db.commit()
    db.refresh(policy_type)
    return policy_type

@router.get("/types", response_model=PremiumPolicyTypeListResponse)
def list_premium_policy_types(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List premium policy types."""
    query = db.query(PremiumPolicyType).filter(
        PremiumPolicyType.company_id == current_user.company_id
    )
    
    total = query.count()
    types = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "premium_policy_types": types,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/types/{type_id}", response_model=PremiumPolicyTypeResponse)
def get_premium_policy_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a premium policy type by ID."""
    policy_type = db.query(PremiumPolicyType).filter(
        PremiumPolicyType.id == type_id,
        PremiumPolicyType.company_id == current_user.company_id
    ).first()
    if not policy_type:
        raise HTTPException(status_code=404, detail="Premium Policy Type not found")
    return policy_type

@router.put("/types/{type_id}", response_model=PremiumPolicyTypeResponse)
def update_premium_policy_type(
    type_id: UUID,
    type_data: PremiumPolicyTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a premium policy type."""
    policy_type = db.query(PremiumPolicyType).filter(
        PremiumPolicyType.id == type_id,
        PremiumPolicyType.company_id == current_user.company_id
    ).first()
    if not policy_type:
        raise HTTPException(status_code=404, detail="Premium Policy Type not found")
    
    update_data = type_data.model_dump(exclude_unset=True)
    
    if 'criteria_ids' in update_data:
        criteria_ids = update_data.pop('criteria_ids')
        criteria = db.query(PremiumPolicyCriteria).filter(
            PremiumPolicyCriteria.id.in_(criteria_ids),
            PremiumPolicyCriteria.company_id == current_user.company_id
        ).all()
        policy_type.criteria = criteria
        
    for field, value in update_data.items():
        setattr(policy_type, field, value)
    
    db.commit()
    db.refresh(policy_type)
    return policy_type

@router.delete("/types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_premium_policy_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a premium policy type."""
    policy_type = db.query(PremiumPolicyType).filter(
        PremiumPolicyType.id == type_id,
        PremiumPolicyType.company_id == current_user.company_id
    ).first()
    if not policy_type:
        raise HTTPException(status_code=404, detail="Premium Policy Type not found")
    
    db.delete(policy_type)
    db.commit()
    return None
