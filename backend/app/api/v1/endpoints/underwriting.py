"""
API endpoints for Underwriting authority and referrals.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.underwriting_intake import StructuredQuoteIntakeRequest, UnderwritingDecisionResponse

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

@router.post("/quote-intake", response_model=UnderwritingDecisionResponse)
def structured_quote_intake(
    intake: StructuredQuoteIntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or re-underwrite a structured automobile quote intake and persist its underwriting snapshot."""
    from app.models.client import Client, client_company
    from app.models.policy_type import PolicyType
    from app.repositories.quote_repository import QuoteRepository
    from app.services.quote_service import QuoteService

    client = db.query(Client).join(
        client_company, Client.id == client_company.c.client_id
    ).filter(
        Client.id == intake.client.client_id,
        client_company.c.company_id == current_user.company_id
    ).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    policy_type = db.query(PolicyType).filter(
        PolicyType.id == intake.cover_options.policy_type_id,
        PolicyType.company_id == current_user.company_id
    ).first()
    if not policy_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy type not found")

    service = UnderwritingService(db)
    quote_id = intake.quote_id

    try:
        if intake.persist_quote and quote_id is None:
            quote_service = QuoteService(QuoteRepository(db))
            quote = quote_service.create_quote(
                company_id=current_user.company_id,
                client_id=intake.client.client_id,
                policy_type_id=intake.cover_options.policy_type_id,
                coverage_amount=intake.cover_options.coverage_amount,
                risk_factors={"structured_underwriting_intake": intake.model_dump(mode="json")},
                premium_frequency=intake.payment_terms.premium_frequency,
                duration_months=intake.usage.policy_duration_months,
                created_by=current_user.id,
            )
            quote_id = quote.id

        result = service.deterministic_quote_underwriting(
            company_id=current_user.company_id,
            intake=intake.model_dump(mode="python"),
            quote_id=quote_id,
            created_by_id=current_user.id,
            persist=intake.persist_quote,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
