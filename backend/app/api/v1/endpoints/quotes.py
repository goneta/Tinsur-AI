"""
API endpoints for quotes.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    
    result = quote_service.calculate_premium(
        policy_type_id=calculation_request.policy_type_id,
        coverage_amount=calculation_request.coverage_amount,
        risk_factors=calculation_request.risk_factors,
        duration_months=calculation_request.duration_months,
        company_id=current_user.company_id
    )
    
    return result


@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote(
    quote_data: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new quote."""
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    try:
        quote = quote_service.create_quote(
            company_id=current_user.company_id,
            client_id=quote_data.client_id,
            policy_type_id=quote_data.policy_type_id,
            coverage_amount=quote_data.coverage_amount,
            risk_factors=quote_data.details or {},
            premium_frequency=quote_data.premium_frequency,
            duration_months=quote_data.duration_months,
            discount_percent=quote_data.discount_percent,
            created_by=quote_data.created_by or current_user.id,
            pos_location_id=quote_data.pos_location_id or current_user.pos_location_id
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
    
    skip = (page - 1) * page_size
    quotes, total = repo.get_by_company(
        company_id=current_user.company_id,
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
    Repo = QuoteRepository(db)
    
    quote = repo.get_by_id(quote_id)
    if not quote or quote.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    # Update fields
    for field, value in quote_data.model_dump(exclude_unset=True).items():
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
    
    # Accept the quote first if not already accepted
    if quote.status != 'accepted':
        quote_service = QuoteService(quote_repo)
        quote_service.accept_quote(quote_id)
    
    # Create policy from quote
    policy = policy_service.create_from_quote(
        quote_id=quote_id,
        start_date=conversion_data.start_date,
        created_by=current_user.id
    )
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create policy from quote"
        )
    
    return {
        "message": "Quote converted to policy successfully",
        "policy_id": str(policy.id),
        "policy_number": policy.policy_number
    }


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
