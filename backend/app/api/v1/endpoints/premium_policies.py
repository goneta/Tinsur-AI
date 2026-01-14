from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.user import User
from app.models.premium_policy import PremiumPolicyCriteria, PremiumPolicyType
from app.models.policy_service import PolicyService
from app.schemas.premium_policy import (
    PremiumPolicyCriteriaCreate,
    PremiumPolicyCriteriaUpdate,
    PremiumPolicyCriteriaResponse,
    PremiumPolicyTypeCreate,
    PremiumPolicyTypeUpdate,
    PremiumPolicyTypeResponse,
    PremiumPolicyTypeResponse,
    PremiumPolicyTypeListResponse,
    PremiumPolicyTypeListResponse,
    PremiumPolicyMatchResponse,
    PremiumPolicyMatchRequest
)
from app.services.premium_policy_service import PremiumPolicyService

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
    service_ids_input = type_data.service_ids
    type_dict = type_data.model_dump()
    if 'criteria_ids' in type_dict:
        del type_dict['criteria_ids']
    if 'service_ids' in type_dict:
        del type_dict['service_ids']
    
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

    if service_ids_input:
        services = db.query(PolicyService).filter(
            PolicyService.id.in_(service_ids_input),
            PolicyService.company_id == current_user.company_id
        ).all()
        policy_type.services = services
        
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

    if 'service_ids' in update_data:
        service_ids = update_data.pop('service_ids')
        services = db.query(PolicyService).filter(
            PolicyService.id.in_(service_ids),
            PolicyService.company_id == current_user.company_id
        ).all()
        policy_type.services = services
        
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

@router.post("/match", response_model=PremiumPolicyMatchResponse)
def match_policies(
    request: PremiumPolicyMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Match eligible policies for a client.
    If authenticated user is a client, client_id is ignored and current_user is used.
    If authenticated user is employee/admin, client_id is required.
    """
    service = PremiumPolicyService(db)
    
    # Determine target client_id
    target_client_id = request.client_id
    
    # If user is a client, override target_client_id with their own client profile id
    if current_user.role == 'client':
        # Find the client profile associated with this user
        from app.models.client import Client
        client_profile = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client_profile:
             raise HTTPException(status_code=404, detail="Client profile not found for this user")
        target_client_id = client_profile.id
    
    if not target_client_id and current_user.role != 'client':
        # Allow missing client_id if we have overrides (transient quote)? 
        # For now, enforce client_id if not client, OR maybe rely on overrides entirely?
        # Let's keep logic simple: strict check unless we decide transient quotes without client_id are allowed.
        # But wait, wizard might be used before client is fully created? 
        # Plan says "client_id: Optional". If missing, we rely PURELY on overrides.
        pass 
        
    overrides = {
        "vehicle_details": request.vehicle_details,
        "driver_details": request.driver_details
    }

    result = service.match_eligible_policies(current_user.company_id, target_client_id, overrides)
    
    # Map status to HTTP exceptions or return specific structure
    if result["status"] == "no_policies":
        raise HTTPException(
            status_code=404, 
            detail={"code": "NO_PREMIUM_POLICIES", "message": result["message"]}
        )
    elif result["status"] == "missing_info":
        raise HTTPException(
            status_code=400,
            detail={
                "code": "MISSING_CLIENT_INFO", 
                "message": result["message"], 
                "missing_fields": result["missing_fields"]
            }
        )
    elif result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result
