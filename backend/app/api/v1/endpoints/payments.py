"""
API endpoints for payments.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentProcessRequest,
    PaymentRefundRequest,
    WebhookPayload,
    PaymentReconciliationRequest,
    PaymentReconciliationResponse
)
from app.repositories.payment_repository import PaymentRepository
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.services.payment_service import PaymentService
from app.services.premium_service import PremiumService
from app.services.payment_ledger_reconciliation_service import PaymentLedgerReconciliationService

router = APIRouter()


@router.post("/process", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def process_payment(
    payment_request: PaymentProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process a new payment."""
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    # Get policy to verify ownership and get client
    from app.repositories.policy_repository import PolicyRepository
    policy_repo = PolicyRepository(db)
    policy = policy_repo.get_by_id(payment_request.policy_id)
    
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Create payment
    payment = payment_service.create_payment(
        company_id=current_user.company_id,
        policy_id=payment_request.policy_id,
        client_id=policy.client_id,
        amount=payment_request.amount,
        payment_method=payment_request.payment_details.get('method'),
        payment_gateway=payment_request.payment_details.get('gateway'),
        metadata=payment_request.payment_details
    )
    
    # Process the payment
    processed_payment = payment_service.process_payment(
        payment_id=payment.id,
        payment_details=payment_request.payment_details,
        actor_id=current_user.id,
        actor_roles=[str(getattr(current_user, "role", ""))],
        payment_live_mode=bool(payment_request.payment_details.get("live_mode"))
    )
    
    # If successful, update premium schedule and award loyalty points
    if processed_payment.status == 'completed':
        schedule_repo = PremiumScheduleRepository(db)
        premium_service = PremiumService(schedule_repo)
        
        # Find pending schedule for this policy and mark as paid
        pending_schedules = schedule_repo.get_pending_by_policy(payment_request.policy_id)
        if pending_schedules:
            premium_service.mark_schedule_as_paid(
                schedule_id=pending_schedules[0].id,
                payment_id=processed_payment.id,
                amount=payment_request.amount
            )
            
        # Award loyalty points
        from app.services.loyalty_service import LoyaltyService
        loyalty_service = LoyaltyService(db)
        loyalty_service.award_points(
            client_id=policy.client_id,
            amount=payment_request.amount,
            reason=f"Payment for policy {policy.policy_number}"
        )
    
    return processed_payment


@router.get("/", response_model=PaymentListResponse)
def list_payments(
    client_id: Optional[UUID] = None,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List payments with filters."""
    repo = PaymentRepository(db)
    
    skip = (page - 1) * page_size
    
    if client_id:
        payments, total = repo.get_by_client(client_id, skip, page_size)
    else:
        payments, total = repo.get_by_company(
            company_id=current_user.company_id,
            status=status,
            payment_method=payment_method,
            skip=skip,
            limit=page_size
        )
    
    return {
        "payments": payments,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/pending", response_model=List[PaymentResponse])
def get_pending_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending payments."""
    repo = PaymentRepository(db)
    payments, _ = repo.get_by_company(
        company_id=current_user.company_id,
        status='pending',
        skip=0,
        limit=1000
    )
    return payments


@router.get("/failed", response_model=List[PaymentResponse])
def get_failed_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all failed payments."""
    repo = PaymentRepository(db)
    payments = repo.get_failed_payments(current_user.company_id)
    return payments



@router.get("/policy/{policy_id}", response_model=List[PaymentResponse])
def get_payments_by_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific policy."""
    repo = PaymentRepository(db)
    # Verify policy access
    from app.repositories.policy_repository import PolicyRepository
    policy_repo = PolicyRepository(db)
    policy = policy_repo.get_by_id(policy_id)
    
    if not policy or policy.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
        
    payments = repo.get_by_policy(policy_id)
    return payments


@router.post("/reconcile", response_model=PaymentReconciliationResponse)
def reconcile_payments(
    request: PaymentReconciliationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reconcile completed payments against gateway transactions and ledger postings."""
    if request.end_date < request.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be on or after start_date"
        )

    service = PaymentLedgerReconciliationService(db, PaymentRepository(db))
    try:
        return service.reconcile_payments(
            current_user.company_id,
            request.start_date.date(),
            request.end_date.date(),
            auto_post_missing=request.auto_post_missing,
            creator_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a payment by ID."""
    repo = PaymentRepository(db)
    
    payment = repo.get_by_id(payment_id)
    if not payment or payment.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: UUID,
    refund_data: PaymentRefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refund a payment."""
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    payment = payment_repo.get_by_id(payment_id)
    if not payment or payment.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    try:
        refunded_payment = payment_service.refund_payment(
            payment_id=payment_id,
            refund_amount=refund_data.refund_amount,
            reason=refund_data.reason,
            actor_id=current_user.id,
            actor_roles=[str(getattr(current_user, "role", ""))],
            payment_live_mode=True
        )
        return refunded_payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/webhooks/stripe", status_code=status.HTTP_200_OK)
def stripe_webhook(
    payload: WebhookPayload = Body(...),
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events."""
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    payment_service.handle_webhook(
        gateway='stripe',
        payload=payload.model_dump()
    )
    
    return {"status": "received"}


@router.post("/webhooks/mobile-money", status_code=status.HTTP_200_OK)
def mobile_money_webhook(
    payload: WebhookPayload = Body(...),
    db: Session = Depends(get_db)
):
    """Handle Mobile Money webhook events."""
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    payment_service.handle_webhook(
        gateway='mobile_money',
        payload=payload.model_dump()
    )
    
    return {"status": "received"}
