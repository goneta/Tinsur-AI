"""
API endpoints for managing sales commissions.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import dependencies as deps
from app.models.user import User
from app.schemas.commission import CommissionSchema, CommissionUpdate
from app.repositories.commission_repository import CommissionRepository
from app.services.commission_service import CommissionService

router = APIRouter()


@router.get("/", response_model=List[CommissionSchema])
def list_commissions(
    agent_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieve commissions with optional filters."""
    repo = CommissionRepository(db)
    
    # If not admin/manager, can only see own commissions
    filter_agent_id = agent_id
    if current_user.role not in ['super_admin', 'company_admin', 'manager']:
        filter_agent_id = current_user.id
        
    commissions, _ = repo.get_by_company(
        company_id=current_user.company_id,
        agent_id=filter_agent_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return commissions


@router.get("/{commission_id}", response_model=CommissionSchema)
def get_commission(
    commission_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific commission record."""
    repo = CommissionRepository(db)
    commission = repo.get_by_id(commission_id)
    
    if not commission or commission.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Commission not found")
        
    # Check access
    if current_user.role not in ['super_admin', 'company_admin', 'manager'] and commission.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this commission")
        
    return commission


@router.put("/{commission_id}", response_model=CommissionSchema)
def update_commission(
    commission_id: UUID,
    commission_in: CommissionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_admin), # Only admin can update (e.g. mark as paid)
):
    """Update a commission (e.g., mark as paid)."""
    repo = CommissionRepository(db)
    service = CommissionService(repo)
    
    commission = repo.get_by_id(commission_id)
    if not commission or commission.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Commission not found")
    
    if commission_in.status == 'paid':
        return service.mark_as_paid(commission_id)
    
    # Generic update
    update_data = commission_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(commission, field, value)
    
    return repo.update(commission)
