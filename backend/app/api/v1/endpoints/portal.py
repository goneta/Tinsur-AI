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
from app.core.security import get_password_hash
from app.schemas.policy import PolicyResponse
from app.schemas.payment import PaymentResponse
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

    # Create Client
    client = Client(
        id=uuid.uuid4(),
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
        kyc_status="pending"
    )
    db.add(client)
    db.flush()

    # Create User account for the portal
    user = User(
        id=uuid.uuid4(),
        company_id=company_id,
        email=data["email"],
        password_hash=get_password_hash(data["password"]),
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        role="client",
        is_active=True
    )
    db.add(user)
    
    # Link user to client
    client.user_id = user.id
    
    db.commit()
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
    ).order_by(desc(Payment.payment_date)).offset(skip).limit(limit).all()
    
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
    
    return {
        "active_policies": active_policies_count,
        "open_claims": open_claims_count,
        "next_payment": {
            "amount": next_payment_amount,
            "date": next_payment_date,
            "currency": "FCFA"
        },
        "pending_actions": 1, # Placeholder for now
        "client_name": current_client.first_name or "Client"
    }
