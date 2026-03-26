"""
Claim endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_agent
from app.schemas.claim import ClaimCreate, ClaimUpdate, ClaimResponse
from app.schemas.claim_activity import ClaimActivityCreate, ClaimActivityResponse
from app.services.claim_service import ClaimService
from app.models.user import User
from app.models.claim_activity import ClaimActivity

router = APIRouter()

@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Create a new claim."""
    service = ClaimService(db)
    # Ensure claim is created for user's company
    claim_data.company_id = current_user.company_id
    if not claim_data.created_by:
        claim_data.created_by = current_user.id
    
    try:
        claim = service.create_claim(claim_data)
        return claim
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[ClaimResponse])
async def get_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all claims."""
    service = ClaimService(db)
    claims, total = service.get_claims(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        status=status
    )
    return claims

@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific claim."""
    service = ClaimService(db)
    claim = service.get_claim(claim_id)
    
    if not claim or claim.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    return claim

@router.put("/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: UUID,
    update_data: ClaimUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Update a claim."""
    service = ClaimService(db)
    
    # Check existence and ownership
    claim = service.get_claim(claim_id)
    if not claim or claim.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
        
    updated_claim = await service.update_claim(claim_id, update_data, current_user.id)
    return updated_claim

from typing import List, Optional, Dict, Any

@router.post("/{claim_id}/analyze", response_model=Dict[str, Any])
async def analyze_claim_damage(
    claim_id: UUID,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Trigger AI analysis for claim damage (includes automated fraud check)."""
    service = ClaimService(db)
    
    # Check existence and ownership
    claim = service.get_claim(claim_id)
    if not claim or claim.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
        
    try:
        results = await service.analyze_claim_damage(claim_id, current_user.id)
        
        # Re-fetch claim to get latest fraud updates
        claim = service.repository.get_by_id(claim_id)
        results["fraud_score"] = float(claim.fraud_score)
        results["fraud_details"] = claim.fraud_details
        
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{claim_id}/analyze-fraud", response_model=Dict[str, Any])
async def analyze_claim_fraud(
    claim_id: UUID,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Trigger standalone AI fraud analysis for a claim."""
    service = ClaimService(db)
    
    # Check existence and ownership
    claim = service.get_claim(claim_id)
    if not claim or claim.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
        
    try:
        results = await service.analyze_claim_fraud(claim_id, current_user.id)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{claim_id}/activity", response_model=List[ClaimActivityResponse])
async def list_claim_activity(
    claim_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List activity for a claim."""
    service = ClaimService(db)
    claim = service.get_claim(claim_id)
    if not claim or claim.company_id != current_user.company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    return db.query(ClaimActivity).filter(ClaimActivity.claim_id == claim_id).order_by(ClaimActivity.created_at.desc()).all()


@router.post("/{claim_id}/activity", response_model=ClaimActivityResponse)
async def add_claim_activity(
    claim_id: UUID,
    payload: ClaimActivityCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Add activity to a claim."""
    service = ClaimService(db)
    claim = service.get_claim(claim_id)
    if not claim or claim.company_id != current_user.company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    activity = ClaimActivity(
        claim_id=claim_id,
        user_id=current_user.id,
        action=payload.action,
        notes=payload.notes,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
