"""
API endpoints for quotes.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListResponse,
    QuoteCalculationRequest,
    QuoteCalculationResponse,
    QuoteToPolicyConversion
)
from app.repositories.quote_repository import QuoteRepository
from app.repositories.policy_repository import PolicyRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.services.quote_service import QuoteService
from app.services.policy_service import PolicyService
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/calculate", response_model=QuoteCalculationResponse)
def calculate_quote(
    calculation_request: QuoteCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate premium for a quote using AI-powered risk assessment."""
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    try:
        logger = logging.getLogger("api.quotes")
        logger.info(f"Calculating premium for client {calculation_request.client_id} with policy {calculation_request.policy_type_id} coverage {calculation_request.coverage_amount}")

        from app.models.client import Client, client_company
        client = db.query(Client).join(
            client_company, Client.id == client_company.c.client_id
        ).filter(
            Client.id == calculation_request.client_id,
            client_company.c.company_id == current_user.company_id
        ).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

        
        result = quote_service.calculate_premium(
            policy_type_id=calculation_request.policy_type_id,
            coverage_amount=calculation_request.coverage_amount,
            risk_factors=calculation_request.risk_factors,
            duration_months=calculation_request.duration_months,
            company_id=current_user.company_id,
            financial_overrides=calculation_request.financial_overrides,
            selected_services=calculation_request.selected_services
        )
        return result
    except Exception as e:
        logger.error(f"Error calculating premium: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}"
        )


@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote(
    quote_data: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new quote.
    Authenticated only.
    If policy_type_id is not provided, uses the first active policy type for the company.
    """
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    # Authenticated: Use trusted session data
    company_id = current_user.company_id
    created_by = current_user.id
    pos_location_id = getattr(current_user, 'pos_location_id', None)

    # Ensure client belongs to the same company (multi-tenant isolation)
    from app.models.client import Client, client_company
    client = db.query(Client).join(
        client_company, Client.id == client_company.c.client_id
    ).filter(
        Client.id == quote_data.client_id,
        client_company.c.company_id == company_id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # If policy_type_id not provided, use default (first active policy type for company)
    policy_type_id = quote_data.policy_type_id
    if not policy_type_id:
        from app.models.policy_type import PolicyType
        default_policy_type = db.query(PolicyType).filter(
            PolicyType.company_id == company_id,
            PolicyType.is_active == True
        ).first()
        
        if not default_policy_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active policy types found for your company. Please create a policy type first."
            )
        policy_type_id = default_policy_type.id

    try:
        quote = quote_service.create_quote(
            company_id=company_id,
            client_id=quote_data.client_id,
            policy_type_id=policy_type_id,
            coverage_amount=quote_data.coverage_amount,
            risk_factors=quote_data.details or {},
            premium_frequency=quote_data.premium_frequency,
            duration_months=quote_data.duration_months,
            discount_percent=quote_data.discount_percent,
            created_by=created_by,
            pos_location_id=pos_location_id,
            financial_overrides=quote_data.financial_overrides,
            selected_services=quote_data.selected_services
        )
        return quote
    except Exception as e:
        import traceback
        print(f"Error creating quote: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create quote: {str(e)}"
        )


@router.get("/", response_model=QuoteListResponse)
def list_quotes(
    client_id: Optional[UUID] = None,
    policy_type_id: Optional[UUID] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List quotes with filters."""
    repo = QuoteRepository(db)
    
    company_id = current_user.company_id

    skip = (page - 1) * page_size
    quotes, total = repo.get_by_company(
        company_id=company_id,
        client_id=client_id,
        policy_type_id=policy_type_id,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    return {
        "quotes": quotes,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{quote_id}", response_model=QuoteResponse)
def get_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a quote by ID."""
    repo = QuoteRepository(db)
    
    quote = repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    return quote


@router.put("/{quote_id}", response_model=QuoteResponse)
def update_quote(
    quote_id: UUID,
    quote_data: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a quote."""
    repo = QuoteRepository(db)
    quote_service = QuoteService(repo)

    quote = repo.get_by_id(quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    # Auth: company staff or the owning client
    if current_user.role == "client":
        from app.models.client import Client
        client_profile = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client_profile or quote.client_id != client_profile.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    else:
        if quote.company_id != current_user.company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    data = quote_data.model_dump(exclude_unset=True)

    # Recalculate if selected services are updated
    if "selected_services" in data:
        selected_services = data.pop("selected_services") or []
        return quote_service.recalculate_quote_services(quote, selected_services)

    # Update fields
    for field, value in data.items():
        setattr(quote, field, value)

    return repo.update(quote)


@router.post("/{quote_id}/send", response_model=QuoteResponse)
def send_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send quote to client."""
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    quote = quote_repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    # Mark as sent (in production, this would trigger email/SMS)
    updated_quote = quote_service.mark_as_sent(quote_id)
    
    return updated_quote


@router.post("/{quote_id}/approve", response_model=dict)
def approve_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a quote and automatically convert it to a policy."""
    quote_repo = QuoteRepository(db)
    policy_repo = PolicyRepository(db)
    endorsement_repo = EndorsementRepository(db)
    quote_service = QuoteService(quote_repo)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    quote = quote_repo.get_by_id(quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
        
    #Permission check: Creator, Assigned Agent, or Admin
    if quote.company_id != current_user.company_id:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    # Idempotency Check: If already policy_created or accepted
    if quote.status in ['policy_created', 'accepted', 'approved']:
        # Find existing policy
        policy = policy_repo.get_by_quote_id(quote_id)
        if policy:
             return {
                "message": "Quote already approved",
                "quote_status": quote.status,
                "policy_id": str(policy.id),
                "policy_number": policy.policy_number
            }

    # State check
    # Allow 'draft', 'sent', 'draft_from_client'
    if quote.status not in ['draft', 'sent', 'draft_from_client']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve quote in '{quote.status}' status"
        )

    # 1. Accept Quote after validating the approved underwriting snapshot.
    try:
        accepted_quote = quote_service.accept_quote(quote_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not accepted_quote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote is expired or cannot be accepted"
        )
    
    # 2. Convert to policy using the same validated snapshot.
    from datetime import date
    start_date = date.today()
    
    policy = policy_service.create_from_quote(
        quote_id=quote_id,
        start_date=start_date,
        created_by=current_user.id,
        actor_roles=[str(getattr(current_user, "role", ""))]
    )
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create policy from quote. Confirm the quote has a current approved underwriting snapshot."
        )
        
    return {
        "message": "Quote approved and policy created successfully",
        "quote_status": "policy_created",
        "policy_id": str(policy.id),
        "policy_number": policy.policy_number,
        "underwriting_snapshot_ready": True,
        "payment_required": True,
        "payment_amount": str(policy.premium_amount)
    }


@router.post("/{quote_id}/reject", response_model=QuoteResponse)
def reject_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a quote."""
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    quote = quote_repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
        
    updated_quote = quote_service.reject_quote(quote_id)
    return updated_quote


@router.post("/{quote_id}/archive", response_model=QuoteResponse)
def archive_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a quote."""
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    quote = quote_repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    # Only accepted quotes can be archived? Or any?
    # User Reqt: "Archive icon -> available for Approved / Accepted quotes (approved quotes cannot be deleted)"
    # Implies Archive is FOR accepted quotes.
    if quote.status not in ['accepted', 'policy_created', 'approved']:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted quotes can be archived"
        )
        
    updated_quote = quote_service.archive_quote(quote_id)
    return updated_quote


@router.post("/{quote_id}/convert", response_model=dict, status_code=status.HTTP_201_CREATED)
def convert_quote_to_policy(
    quote_id: UUID,
    conversion_data: QuoteToPolicyConversion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Convert an accepted quote to a policy."""
    quote_repo = QuoteRepository(db)
    policy_repo = PolicyRepository(db)
    endorsement_repo = EndorsementRepository(db)
    policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
    
    quote = quote_repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    quote_service = QuoteService(quote_repo)

    # Accept the quote first if not already accepted, but only after underwriting validation.
    if quote.status not in ['accepted', 'policy_created', 'approved']:
        try:
            accepted_quote = quote_service.accept_quote(quote_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        if not accepted_quote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quote is expired or cannot be accepted"
            )
    else:
        try:
            quote_service.validate_policy_ready_underwriting(quote)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    
    # Create policy from quote. This is idempotent and returns the existing policy when present.
    policy = policy_service.create_from_quote(
        quote_id=quote_id,
        start_date=conversion_data.start_date,
        created_by=current_user.id,
        actor_roles=[str(getattr(current_user, "role", ""))]
    )
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create policy from quote. Confirm the quote has a current approved underwriting snapshot."
        )

    payment = None
    if conversion_data.payment_method:
        payment_service = PaymentService(db, PaymentRepository(db))
        amount = conversion_data.initial_payment_amount or policy.premium_amount
        payment = payment_service.create_payment(
            company_id=policy.company_id,
            policy_id=policy.id,
            client_id=policy.client_id,
            amount=amount,
            payment_method=conversion_data.payment_method,
            payment_gateway=conversion_data.payment_gateway,
            metadata={
                "source": "quote_conversion",
                "quote_id": str(quote_id),
                "underwriting_snapshot_id": str(quote_service.get_underwriting_snapshot(quote_id).id),
                "policy_id": str(policy.id),
            }
        )
        if conversion_data.process_payment:
            details = conversion_data.payment_details or {}
            payment = payment_service.process_payment(
                payment.id,
                details,
                actor_id=current_user.id,
                actor_roles=[str(getattr(current_user, "role", ""))],
                payment_live_mode=bool(details.get("live_mode")),
            )
    
    response = {
        "message": "Quote converted to policy successfully",
        "policy_id": str(policy.id),
        "policy_number": policy.policy_number,
        "quote_status": "policy_created",
        "underwriting_snapshot_ready": True
    }
    if payment:
        response["payment_id"] = str(payment.id)
        response["payment_number"] = payment.payment_number
        response["payment_status"] = payment.status
        response["payment_amount"] = str(payment.amount)
    return response


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a quote."""
    repo = QuoteRepository(db)
    
    quote = repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    repo.delete(quote_id)
    return None


@router.post("/auto-generate/{client_id}")
def auto_generate_quotes(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Auto-generate recommended quotes for a client.
    
    Returns a list of quotes sorted by price (cheapest first).
    Includes recommendation order based on premium amount.
    """
    from app.models.client import Client, client_company
    from app.services.quote_generation_service import QuoteGenerationService
    
    logger = logging.getLogger("api.quotes")
    
    try:
        # Verify client exists and belongs to company
        client = db.query(Client).join(
            client_company, Client.id == client_company.c.client_id
        ).filter(
            Client.id == client_id,
            client_company.c.company_id == current_user.company_id
        ).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Generate quotes
        quote_gen_service = QuoteGenerationService(db)
        recommended_quotes = quote_gen_service.auto_generate_quotes(client_id)
        
        logger.info(f"Auto-generated {len(recommended_quotes)} quotes for client {client_id}")
        
        return {
            "client_id": str(client_id),
            "recommended_quotes": recommended_quotes,
            "total_quotes": len(recommended_quotes)
        }
    except ValueError as e:
        logger.error(f"Validation error generating quotes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error auto-generating quotes: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quotes: {str(e)}"
        )


@router.get("/{quote_id}/details")
def get_quote_details(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full details of a quote including coverage, benefits, and discounts.
    
    Returns comprehensive quote information for display in details modal.
    """
    from app.services.quote_generation_service import QuoteGenerationService
    
    logger = logging.getLogger("api.quotes")
    
    try:
        # Verify quote exists and belongs to company
        repo = QuoteRepository(db)
        quote = repo.get_by_id(quote_id)
        
        if not quote or quote.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        # Get detailed information
        quote_gen_service = QuoteGenerationService(db)
        details = quote_gen_service.get_quote_details(quote_id)
        
        logger.info(f"Retrieved details for quote {quote_id}")
        
        return {
            "quote_id": str(quote_id),
            "details": details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quote details: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quote details: {str(e)}"
        )
