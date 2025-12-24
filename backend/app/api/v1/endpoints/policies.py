"""
API endpoints for policies.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyListResponse,
    PolicyRenewalRequest,
    PolicyCancellationRequest,
    EndorsementCreate,
    EndorsementResponse
)
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.services.policy_service import PolicyService
from app.services.premium_service import PremiumService

router = APIRouter()


@router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new policy."""
    policy_repo = PolicyRepository(db)
    quote_repo = QuoteRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    policy = policy_service.create_policy(
        company_id=current_user.company_id,
        client_id=policy_data.client_id,
        policy_type_id=policy_data.policy_type_id,
        coverage_amount=policy_data.coverage_amount,
        premium_amount=policy_data.premium_amount,
        premium_frequency=policy_data.premium_frequency,
        start_date=policy_data.start_date,
        end_date=policy_data.end_date,
        created_by=current_user.id,
        sales_agent_id=policy_data.sales_agent_id,
        pos_location_id=policy_data.pos_location_id,
        details=policy_data.details
    )
    
    # Generate payment schedule
    schedule_repo = PremiumScheduleRepository(db)
    premium_service = PremiumService(schedule_repo)
    
    duration_months = (policy.end_date.year - policy.start_date.year) * 12 + \
                     (policy.end_date.month - policy.start_date.month)
    
    premium_service.generate_payment_schedule(
        company_id=current_user.company_id,
        policy_id=policy.id,
        total_premium=policy.premium_amount,
        frequency=policy.premium_frequency,
        start_date=policy.start_date,
        duration_months=duration_months
    )
    
    return policy


@router.get("/", response_model=PolicyListResponse)
def list_policies(
    client_id: Optional[UUID] = None,
    policy_type_id: Optional[UUID] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List policies with filters."""
    repo = PolicyRepository(db)
    
    skip = (page - 1) * page_size
    policies, total = repo.get_by_company(
        company_id=current_user.company_id,
        client_id=client_id,
        policy_type_id=policy_type_id,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    return {
        "policies": policies,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/expiring", response_model=List[PolicyResponse])
def get_expiring_policies(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get policies expiring within specified days."""
    repo = PolicyRepository(db)
    policies = repo.get_expiring_soon(current_user.company_id, days)
    return policies


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a policy by ID."""
    repo = PolicyRepository(db)
    
    policy = repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    return policy


@router.get("/{policy_id}/schedule", response_model=dict)
def get_policy_payment_schedule(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment schedule for a policy."""
    policy_repo = PolicyRepository(db)
    schedule_repo = PremiumScheduleRepository(db)
    
    policy = policy_repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    schedules = schedule_repo.get_by_policy(policy_id)
    summary = schedule_repo.get_policy_summary(policy_id)
    
    return {
        "policy_id": str(policy_id),
        "schedules": schedules,
        **summary
    }


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: UUID,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a policy."""
    repo = PolicyRepository(db)
    
    policy = repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Update fields
    for field, value in policy_data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
    
    return repo.update(policy)


@router.post("/{policy_id}/renew", response_model=PolicyResponse)
def renew_policy(
    policy_id: UUID,
    renewal_data: PolicyRenewalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Renew a policy."""
    policy_repo = PolicyRepository(db)
    quote_repo = QuoteRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    policy = policy_repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    renewed_policy = policy_service.renew_policy(
        policy_id=policy_id,
        new_end_date=renewal_data.new_end_date,
        premium_amount=renewal_data.premium_amount,
        coverage_amount=renewal_data.coverage_amount
    )
    
    return renewed_policy


@router.post("/{policy_id}/cancel", response_model=PolicyResponse)
def cancel_policy(
    policy_id: UUID,
    cancellation_data: PolicyCancellationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a policy."""
    policy_repo = PolicyRepository(db)
    quote_repo = QuoteRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    policy = policy_repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    canceled_policy = policy_service.cancel_policy(
        policy_id=policy_id,
        reason=cancellation_data.cancellation_reason
    )
    
    return canceled_policy


@router.post("/{policy_id}/reinstate", response_model=PolicyResponse)
def reinstate_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reinstate a canceled or lapsed policy."""
    policy_repo = PolicyRepository(db)
    quote_repo = QuoteRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    policy = policy_repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
        
    reinstated_policy = policy_service.reinstate_policy(policy_id)
    
    if not reinstated_policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not reinstate policy"
        )
        
    return reinstated_policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a policy (soft delete by changing status)."""
    repo = PolicyRepository(db)
    
    policy = repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Soft delete by setting status to canceled
    policy.status = 'canceled'
    policy.cancellation_reason = "Deleted by admin"
    repo.update(policy)
    
    return None


@router.post("/{policy_id}/endorsements", response_model=EndorsementResponse)
def create_endorsement(
    policy_id: UUID,
    endorsement_data: EndorsementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new endorsement draft."""
    policy_repo = PolicyRepository(db)
    quote_repo = QuoteRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    policy = policy_repo.get_by_id(policy_id)
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
        
    endorsement = policy_service.create_endorsement(
        company_id=current_user.company_id,
        policy_id=policy_id,
        endorsement_type=endorsement_data.endorsement_type,
        changes=endorsement_data.changes,
        premium_adjustment=endorsement_data.premium_adjustment,
        effective_date=endorsement_data.effective_date,
        created_by=current_user.id,
        reason=endorsement_data.reason
    )
    
    if not endorsement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create endorsement"
        )
        
    return endorsement


@router.post("/endorsements/{endorsement_id}/approve", response_model=PolicyResponse)
def approve_endorsement(
    endorsement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve an endorsement and apply to policy."""
    policy_repo = PolicyRepository(db)
    quote_repo = QuoteRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    endorsement = endorsement_repo.get_by_id(endorsement_id)
    if not endorsement or endorsement.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endorsement not found"
        )
        
    policy = policy_service.approve_endorsement(
        endorsement_id=endorsement_id,
        approved_by=current_user.id
    )
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not approve endorsement"
        )
        
    return policy
