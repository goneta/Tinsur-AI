"""
Client Portal endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.dependencies import get_current_client
from app.models.client import Client
from app.models.policy import Policy
from app.models.payment import Payment
from app.models.company import Company
from app.models.user import User
from app.models.claim import Claim
from app.models.referral import Referral
from app.core.security import get_password_hash
from app.schemas.policy import PolicyResponse
from app.schemas.payment import PaymentResponse, PaymentProcessRequest
from app.schemas.claim import ClaimCreate, ClaimResponse
from app.schemas.quote import (
    QuoteCalculationRequest, 
    QuoteCalculationResponse, 
    QuoteCreate, 
    QuoteResponse
)
from app.services.claim_service import ClaimService
from app.services.payment_service import PaymentService
from app.services.quote_service import QuoteService
from app.services.premium_service import PremiumService
from app.services.loyalty_service import LoyaltyService
from app.repositories.payment_repository import PaymentRepository
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.policy_repository import PolicyRepository
import uuid

router = APIRouter()

@router.post("/register")
async def register_client(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Public endpoint for a client to register themselves at a company's portal.
    """
    company_id = data.get("company_id")
    if not company_id:
        # Try to find by subdomain if provided
        subdomain = data.get("subdomain")
        if subdomain:
            company = db.query(Company).filter(Company.subdomain == subdomain).first()
            if company:
                company_id = company.id
    
    if not company_id:
        raise HTTPException(status_code=400, detail="Company identifier required")

    # Check if email exists
    existing_user = db.query(User).filter(User.email == data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create User account for the portal
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        company_id=company_id,
        email=data["email"],
        password_hash=get_password_hash(data["password"]),
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        role="client",
        is_active=True
    )
    db.add(user)
    # Note: User is added to session but not committed yet. 
    # ClientService.create_client will commit the session.

    # Create Client via Service
    from app.services.client_service import ClientService
    from app.schemas.client import ClientCreate
    
    client_data = ClientCreate(
        company_id=company_id,
        client_type=data.get("client_type", "individual"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        business_name=data.get("business_name"),
        email=data["email"],
        phone=data.get("phone"),
        date_of_birth=data.get("date_of_birth"),
        nationality=data.get("nationality"),
        id_number=data.get("id_number"),
        kyc_status="pending",
        
        # Identity fields for Driver Card mapping
        driving_licence_number=data.get("driving_licence_number"), 
        # Note: If portal form sends 'license_number' we might need to map it. 
        # Standardize on 'driving_licence_number' for Client model as per schema.
        
        address=data.get("address"),
        city=data.get("city"),
        country=data.get("country", "Côte d'Ivoire")
    )
    
    service = ClientService(db)
    client = await service.create_client(client_data, user_id=user_id)
    
    # Process referral if exists
    referral_code = data.get("referral_code")
    if referral_code:
        referral = db.query(Referral).filter(
            Referral.referral_code == referral_code,
            Referral.company_id == company_id,
            Referral.status == "pending"
        ).first()
        if referral:
            referral.referred_client_id = client.id
            referral.status = "converted" # Or keep pending until first payment? 
            # Plan says: "In process_payment, mark referral as converted and award points... on first payment"
            # So I'll just link the referred_client_id here.
            referral.converted_at = datetime.utcnow()
            db.add(referral)
            db.commit() # Commit referral changes if any
    
    # Ensure all committed
    # ClientService commits client (and users in session).
    # If we added referral changes after, ensuring commit.
    pass
    return {"message": "Registration successful", "client_id": str(client.id)}


@router.get("/policies", response_model=List[PolicyResponse])
async def get_my_policies(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all policies for the current client.
    """
    policies = db.query(Policy).filter(
        Policy.client_id == current_client.id
    ).order_by(desc(Policy.created_at)).offset(skip).limit(limit).all()
    
    return policies


@router.get("/policies/{id}", response_model=PolicyResponse)
async def get_my_policy(
    id: str,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Get a specific policy for the current client.
    """
    policy = db.query(Policy).filter(
        Policy.id == id,
        Policy.client_id == current_client.id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    return policy


@router.get("/payments", response_model=List[PaymentResponse])
async def get_my_payments(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client),
    skip: int = 0,
    limit: int = 100
):
    """
    Get payment history for the current client.
    """
    payments = db.query(Payment).filter(
        Payment.client_id == current_client.id
    ).order_by(desc(Payment.created_at)).offset(skip).limit(limit).all()
    
    return payments


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Get summary stats for client dashboard.
    """
    active_policies = db.query(Policy).filter(
        Policy.client_id == current_client.id,
        Policy.status == "active"
    ).all()
    
    active_policies_count = len(active_policies)
    
    open_claims_count = db.query(Claim).filter(
        Claim.client_id == current_client.id,
        Claim.status.in_(["submitted", "under_review", "approved"])
    ).count()
    
    # Logic for next payment: simple proxy using nearest end_date for now
    next_payment_amount = 0
    next_payment_date = None
    
    if active_policies:
        # Sort by end_date (renewal/next premium)
        sorted_policies = sorted(active_policies, key=lambda p: p.end_date)
        next_policy = sorted_policies[0]
        next_payment_amount = float(next_policy.premium_amount)
        next_payment_date = next_policy.end_date.isoformat()
    
    policies_data = []
    for p in active_policies:
        details = p.details or {}
        
        vehicles = details.get("vehicles", [])
        if not vehicles:
            if current_client.automobile_details:
                vehicles = [{
                    "make": current_client.automobile_details.vehicle_make or "KIA",
                    "model": current_client.automobile_details.vehicle_model or "CEE'D 2 CRDI (126)",
                    "registration": current_client.automobile_details.vehicle_registration or "LG13MWC",
                    "year": current_client.automobile_details.vehicle_year
                }]
            else:
                vehicles = [{
                    "make": "KIA",
                    "model": "CEE'D 2 CRDI (126)",
                    "registration": "LG13MWC",
                    "year": 2013
                }]
        
        drivers = details.get("drivers", [])
        if not drivers:
            drivers = [{
                "name": f"{current_client.first_name} {current_client.last_name}",
                "type": "main"
            }]

        policies_data.append({
            "id": str(p.id),
            "policy_number": p.policy_number,
            "renewal_date": p.end_date.isoformat(),
            "start_date": p.start_date.isoformat(),
            "vehicles": vehicles,
            "drivers": drivers,
            "cover_type": details.get("cover_type", "Comprehensive"),
            "usage": details.get("usage", "Social Domestic and Pleasure, including Commuting"),
            "mileage": details.get("mileage", 3000),
            "parked_overnight": details.get("parked_overnight", "Driveway"),
            "postcode": details.get("postcode", "B69 1PE"),
            "ncd_years": details.get("ncd_years", 7),
            "ncd_protected": details.get("ncd_protected", True),
            "voluntary_excess": details.get("voluntary_excess", 250),
            "compulsory_excess": details.get("compulsory_excess", 200),
            "policy_type_name": p.policy_type.name if hasattr(p, 'policy_type') and p.policy_type else "Bronze Cover",
            "services": [
                {
                    "id": str(s.id),
                    "name_en": s.name_en,
                    "name_fr": s.name_fr,
                    "price": float(s.default_price)
                } for s in p.services
            ]
        })

    # Fetch loyalty info
    loyalty_service = LoyaltyService(db)
    loyalty = loyalty_service.get_or_create_loyalty(current_client.id)
    
    # Fetch company info
    company = db.query(Company).filter(Company.id == current_client.company_id).first()
    insurance_company = company.name if company else "Tesco Underwriting Limited"
    insurance_company_phone = company.phone if company and company.phone else "0345 677 3377"
    
    premium_tier = "Bronze"
    policy_type_name = "Bronze Cover"
    if active_policies:
        p = active_policies[0]
        if hasattr(p, 'policy_type') and p.policy_type:
            policy_type_name = p.policy_type.name
            if "gold" in p.policy_type.name.lower(): premium_tier = "Gold"
            elif "silver" in p.policy_type.name.lower(): premium_tier = "Silver"
            else: premium_tier = "Bronze"

    return {
        "active_policies_count": active_policies_count,
        "open_claims": open_claims_count,
        "next_payment": {
            "amount": next_payment_amount,
            "date": next_payment_date,
            "currency": "FCFA"
        },
        "pending_actions": 1, 
        "client_name": current_client.first_name or "Client",
        "loyalty": {
            "points": loyalty.points_balance,
            "tier": loyalty.tier
        },
        "premium_tier": premium_tier,
        "policy_type_name": policy_type_name,
        "insurance_company": insurance_company,
        "insurance_company_phone": insurance_company_phone,
        "primary_policy": policies_data[0] if policies_data else None,
        "policies": policies_data
    }


@router.post("/claims", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_my_claim(
    claim_data: ClaimCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Allow a client to file a claim for one of their policies.
    """
    # Verify policy belongs to client
    policy = db.query(Policy).filter(
        Policy.id == claim_data.policy_id,
        Policy.client_id == current_client.id
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found or does not belong to you")
        
    service = ClaimService(db)
    claim_data.company_id = current_client.company_id
    
    try:
        claim = service.create_claim(claim_data)
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/process", response_model=PaymentResponse)
async def process_my_payment(
    payment_request: PaymentProcessRequest,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Allow a client to pay for their policy.
    """
    # Verify policy belongs to client
    policy = db.query(Policy).filter(
        Policy.id == payment_request.policy_id,
        Policy.client_id == current_client.id
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found or does not belong to you")
        
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(db, payment_repo)
    
    # Create and process payment
    payment = payment_service.create_payment(
        company_id=current_client.company_id,
        policy_id=payment_request.policy_id,
        client_id=current_client.id,
        amount=payment_request.amount,
        payment_method=payment_request.payment_details.get('method'),
        payment_gateway=payment_request.payment_details.get('gateway'),
        metadata=payment_request.payment_details
    )
    
    processed_payment = payment_service.process_payment(
        payment_id=payment.id,
        payment_details=payment_request.payment_details
    )
    
    if processed_payment.status == 'completed':
        # Update schedule
        schedule_repo = PremiumScheduleRepository(db)
        premium_service = PremiumService(schedule_repo)
        pending_schedules = schedule_repo.get_pending_by_policy(payment_request.policy_id)
        if pending_schedules:
            premium_service.mark_schedule_as_paid(
                schedule_id=pending_schedules[0].id,
                payment_id=processed_payment.id,
                amount=payment_request.amount
            )
            
        # Award loyalty points
        loyalty_service = LoyaltyService(db)
        loyalty_service.award_points(
            client_id=current_client.id,
            amount=payment_request.amount,
            reason=f"Payment for policy {policy.policy_number}"
        )
        
    return processed_payment


@router.post("/quotes/calculate", response_model=QuoteCalculationResponse)
async def calculate_my_quote(
    calculation_request: QuoteCalculationRequest,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Calculate a quote for the client.
    """
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    result = quote_service.calculate_premium(
        policy_type_id=calculation_request.policy_type_id,
        coverage_amount=calculation_request.coverage_amount,
        risk_factors=calculation_request.risk_factors,
        duration_months=calculation_request.duration_months,
        company_id=current_client.company_id,
        selected_services=calculation_request.selected_services,
        financial_overrides=calculation_request.financial_overrides
    )
    return result


@router.post("/quotes", response_model=QuoteResponse)
async def create_my_quote(
    quote_data: QuoteCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Save a quote for the client.
    """
    quote_repo = QuoteRepository(db)
    quote_service = QuoteService(quote_repo)
    
    quote_data.client_id = current_client.id
    
    try:
        quote = quote_service.create_quote(
            company_id=current_client.company_id,
            client_id=current_client.id,
            policy_type_id=quote_data.policy_type_id,
            coverage_amount=quote_data.coverage_amount,
            risk_factors=quote_data.details or {},
            premium_frequency=quote_data.premium_frequency,
            duration_months=quote_data.duration_months,
            discount_percent=quote_data.discount_percent,
            created_by=current_client.user_id,
            selected_services=quote_data.selected_services,
            financial_overrides=quote_data.financial_overrides
        )
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create quote: {str(e)}")
# --- Support Tickets ---
from app.models.ticket import Ticket, TicketMessage
from app.schemas import ticket as ticket_schemas
import random 

@router.post("/tickets", response_model=ticket_schemas.Ticket)
async def create_my_ticket(
    ticket_data: ticket_schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Create a support ticket.
    """
    ticket = Ticket(
        company_id=current_client.company_id,
        client_id=current_client.id,
        ticket_number=f"TKT-{random.randint(10000, 99999)}",
        category=ticket_data.category,
        priority=ticket_data.priority,
        subject=ticket_data.subject,
        description=ticket_data.description,
        status='open'
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/tickets", response_model=List[ticket_schemas.Ticket])
async def get_my_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    List my support tickets.
    """
    tickets = db.query(Ticket).filter(
        Ticket.client_id == current_client.id
    ).order_by(desc(Ticket.created_at)).offset(skip).limit(limit).all()
    return tickets

@router.get("/tickets/{ticket_id}", response_model=ticket_schemas.Ticket)
async def get_my_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Get a specific ticket with messages.
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.client_id == current_client.id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Filter out internal messages safely
    # We can't easily mutate the ORM relationship without DB session impact sometimes,
    # but for read-only return it's okay to create a temporary object or use Pydantic helpers.
    # Easiest: return a dict that matches schema
    
    # We rely on Pydantic's from_attributes=True.
    # Let's manually filter messages.
    visible_messages = [m for m in ticket.messages if not m.is_internal]
    
    # Check if lazy load happened? `ticket.messages` access triggers it.
    
    # Modify the object for the response? 
    # ticket.messages = visible_messages  <-- might trigger SQLAlchemy warning or pending change
    # Better to construct response explicitly if possible.
    # Or just return a wrapper.
    
    return {
        "id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "company_id": ticket.company_id,
        "client_id": ticket.client_id,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "subject": ticket.subject,
        "description": ticket.description,
        "assigned_to": ticket.assigned_to,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "resolved_at": ticket.resolved_at,
        "messages": visible_messages
    }

@router.post("/tickets/{ticket_id}/reply", response_model=ticket_schemas.TicketMessage)
async def reply_my_ticket(
    ticket_id: str,
    message_data: ticket_schemas.TicketMessageCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Reply to a ticket.
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.client_id == current_client.id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Create message
    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=current_client.id,
        sender_type='client',
        message=message_data.message,
        is_internal=False # Clients can't make internal notes
    )
    db.add(message)
    
    # If ticket was resolved/closed, reopen it?
    if ticket.status in ['resolved', 'closed']:
        ticket.status = 'open'
        
    db.commit()
    db.refresh(message)
    return message


# --- Referrals ---
from app.services.referral_service import ReferralService
from app.schemas import referral as referral_schemas
from app.models.referral import Referral

@router.post("/referrals", response_model=referral_schemas.Referral)
async def create_my_referral(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Generate a referral code for the current client.
    """
    service = ReferralService(db)
    return service.create_referral(
        company_id=current_client.company_id,
        referrer_client_id=current_client.id
    )

@router.get("/referrals/stats")
async def get_my_referral_stats(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Get referral statistics for the current client.
    """
    # Custom stats for the client
    referrals = db.query(Referral).filter(
        Referral.company_id == current_client.company_id,
        Referral.referrer_client_id == current_client.id
    ).all()
    
    total_earned = sum(r.reward_amount or 0 for r in referrals if r.reward_paid)
    pending_count = sum(1 for r in referrals if r.status == 'pending')
    converted_count = sum(1 for r in referrals if r.status == 'converted' or r.status == 'rewarded')
    
    # Check if they have a code
    my_referral = db.query(Referral).filter(
        Referral.company_id == current_client.company_id,
        Referral.referrer_client_id == current_client.id
    ).first()
    
    return {
        "referral_code": my_referral.referral_code if my_referral else None,
        "total_earned": total_earned,
        "pending_count": pending_count,
        "converted_count": converted_count,
        "total_referrals": len(referrals)
    }

@router.get("/referrals", response_model=List[referral_schemas.Referral])
async def get_my_referrals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    List clients I have referred.
    """
    return db.query(Referral).filter(
        Referral.company_id == current_client.company_id,
        Referral.referrer_client_id == current_client.id
    ).order_by(desc(Referral.created_at)).offset(skip).limit(limit).all()


# --- Account Settings ---
from app.models.user import User
from app.core.security import verify_password
from pydantic import BaseModel, EmailStr

class ProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class TwoFactorUpdate(BaseModel):
    enabled: bool

@router.get("/profile", response_model=dict)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Get client profile details.
    """
    # Fetch linked user for MFA status
    mfa_enabled = False
    if current_client.user_id:
        user = db.query(User).filter(User.id == current_client.user_id).first()
        if user:
            mfa_enabled = user.mfa_enabled or False

    return {
        "first_name": current_client.first_name,
        "last_name": current_client.last_name,
        "email": current_client.email,
        "phone": current_client.phone,
        "address": current_client.address,
        "city": current_client.city,
        "mfa_enabled": mfa_enabled,
        "client_type": current_client.client_type
    }

@router.put("/profile", response_model=dict)
async def update_my_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Update client profile details.
    """
    # Update Client record
    current_client.first_name = profile_data.first_name
    current_client.last_name = profile_data.last_name
    current_client.phone = profile_data.phone
    current_client.address = profile_data.address
    current_client.city = profile_data.city
    
    # Update User record if linked
    if current_client.user_id:
        user = db.query(User).filter(User.id == current_client.user_id).first()
        if user:
            user.first_name = profile_data.first_name
            user.last_name = profile_data.last_name
            user.phone = profile_data.phone
            
    db.commit()
    return {"message": "Profile updated successfully"}

@router.post("/security/password", response_model=dict)
async def change_my_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Change client password.
    """
    if not current_client.user_id:
         raise HTTPException(status_code=400, detail="No user account linked to this client profile")
         
    user = db.query(User).filter(User.id == current_client.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")
        
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/security/2fa", response_model=dict)
async def toggle_my_2fa(
    data: TwoFactorUpdate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Enable or Disable Two-Factor Authentication.
    """
    if not current_client.user_id:
         raise HTTPException(status_code=400, detail="No user account linked")
         
    user = db.query(User).filter(User.id == current_client.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")
        
    user.mfa_enabled = data.enabled
    
    # In a real implementation, we would generate and return a secret/QR code here if enabling
    # For now, we just toggle the flag as requested "optional" feature starter.
    
    db.commit()
    status_msg = "enabled" if data.enabled else "disabled"
    return {"message": f"Two-factor authentication {status_msg}", "mfa_enabled": user.mfa_enabled}

@router.delete("/account", response_model=dict)
async def delete_my_account(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    """
    Request account deletion (Soft Delete).
    """
    # Soft delete client
    current_client.status = 'inactive'
    
    # Soft delete user
    if current_client.user_id:
        user = db.query(User).filter(User.id == current_client.user_id).first()
        if user:
            user.is_active = False
            
    db.commit()
    return {"message": "Account successfully deactivated. You will now be logged out."}
