"""
API endpoints for Underwriting authority and referrals.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.underwriting_service import UnderwritingService

router = APIRouter()

class UnderwritingDecision(BaseModel):
    status: str # 'approved', 'rejected'
    decision_notes: str

@router.get("/referrals/pending")
def get_pending_referrals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "company_admin", "manager", "accountant"]))
):
    """Get all pending underwriting referrals for the company."""
    service = UnderwritingService(db)
    return service.get_pending_referrals(current_user.company_id)

@router.post("/referrals/{referral_id}/decide")
def decide_on_referral(
    referral_id: UUID,
    decision: UnderwritingDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "company_admin", "manager"]))
):
    """Approve or reject an underwriting referral."""
    service = UnderwritingService(db)
    try:
        quote = service.process_referral_decision(
            referral_id=referral_id,
            decided_by_id=current_user.id,
            status=decision.status,
            notes=decision.decision_notes
        )
        return {"status": "success", "quote_status": quote.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-authority")
def get_my_authority(
    current_user: User = Depends(get_current_user)
):
    """Get the current user's underwriting authority limit."""
    return {
        "user_id": current_user.id,
        "role": current_user.role,
        "underwriting_limit": float(current_user.underwriting_limit) if current_user.underwriting_limit else None,
        "has_unlimited_authority": current_user.role in ['super_admin', 'company_admin']
    }
