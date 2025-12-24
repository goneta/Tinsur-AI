from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import uuid

from app.core import dependencies as deps
from app.models.referral import Referral
from app.schemas import referral as schemas

router = APIRouter()

@router.post("/", response_model=schemas.Referral)
def create_referral(
    *,
    db: Session = Depends(deps.get_db),
    referral_in: schemas.ReferralCreate,
    current_user = Depends(deps.get_current_active_user),
):
    """
    Create a new referral (generate code).
    """
    code = f"REF-{str(uuid.uuid4())[:8].upper()}"
    
    referral = Referral(
        company_id=current_user.company_id,
        referrer_client_id=referral_in.referrer_client_id,
        referral_code=code,
        status="pending"
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)
    return referral

@router.get("/", response_model=List[schemas.Referral])
def read_referrals(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve referrals.
    """
    referrals = db.query(Referral).filter(
        Referral.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    return referrals

@router.get("/stats")
def read_referral_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Get company-wide referral statistics.
    """
    from sqlalchemy import func
    
    total_rewards = db.query(func.sum(Referral.reward_amount)).filter(
        Referral.company_id == current_user.company_id,
        Referral.reward_paid == True
    ).scalar() or 0
    
    pending_conversions = db.query(Referral).filter(
        Referral.company_id == current_user.company_id,
        Referral.status == "pending"
    ).count()

    converted_count = db.query(Referral).filter(
        Referral.company_id == current_user.company_id,
        Referral.status == "converted"
    ).count()
    
    return {
        "total_rewards": total_rewards,
        "pending_conversions": pending_conversions,
        "converted_count": converted_count
    }
