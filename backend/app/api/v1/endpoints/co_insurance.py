
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from decimal import Decimal

from app.core.database import get_db
from app.models.co_insurance import CoInsuranceShare
from app.models.policy import Policy
from app.models.company import Company
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{policy_id}/shares", response_model=List[dict])
def get_policy_shares(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all co-insurance participants for a policy."""
    shares = db.query(CoInsuranceShare).filter(CoInsuranceShare.policy_id == policy_id).all()
    
    return [
        {
            "id": s.id,
            "company_id": s.company_id,
            "company_name": s.company.name,
            "share_percentage": float(s.share_percentage),
            "fee_percentage": float(s.fee_percentage),
            "notes": s.notes,
            "created_at": s.created_at
        }
        for s in shares
    ]

@router.post("/{policy_id}/shares")
def add_policy_share(
    policy_id: uuid.UUID,
    company_id: uuid.UUID,
    share_percentage: float,
    fee_percentage: float = 0,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a participant to a co-insured policy."""
    # 1. Verify policy and company exist
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # 2. Check total shares don't exceed 100%
    existing_shares_sum = db.query(Decimal).select_from(CoInsuranceShare).filter(CoInsuranceShare.policy_id == policy_id).with_entities(CoInsuranceShare.share_percentage).all()
    total = sum([s[0] for s in existing_shares_sum]) + Decimal(str(share_percentage))
    
    if total > 100:
        raise HTTPException(status_code=400, detail=f"Total shares ({total}%) cannot exceed 100%")

    # 3. Create share
    share = CoInsuranceShare(
        policy_id=policy_id,
        company_id=company_id,
        share_percentage=share_percentage,
        fee_percentage=fee_percentage,
        notes=notes
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    
    return share

@router.delete("/shares/{share_id}")
def remove_policy_share(
    share_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a participant from co-insurance."""
    share = db.query(CoInsuranceShare).filter(CoInsuranceShare.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
        
    db.delete(share)
    db.commit()
    
    return {"status": "success", "message": "Participant removed"}

@router.get("/my-policies", response_model=List[dict])
def list_my_coinsurance_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all policies where the current company is a co-insurance participant (including lead)."""
    # 1. Policies where I am the lead insurer (company_id on Policy table) AND have shares
    lead_policies = db.query(Policy).join(CoInsuranceShare).filter(
        Policy.company_id == current_user.company_id
    ).all()
    
    # 2. Policies where I am a participant (company_id on CoInsuranceShare table) but NOT lead
    participant_shares = db.query(CoInsuranceShare).filter(
        CoInsuranceShare.company_id == current_user.company_id,
        # Exclude those already found in lead_policies if needed, 
        # but simpler to just query policies directly via relationship
    ).all()
    
    results = []
    seen_ids = set()
    
    # Add Lead Policies
    for p in lead_policies:
        if p.id not in seen_ids:
            results.append({
                "id": p.id,
                "policy_number": p.policy_number,
                "lead_company": p.company.name,
                "is_lead": True,
                "my_share": 100 - sum([float(s.share_percentage) for s in p.co_insurance_shares]), # Simplified
                "status": p.status,
                "premium_amount": float(p.premium_amount),
                "start_date": p.start_date,
                "end_date": p.end_date
            })
            seen_ids.add(p.id)
            
    # Add Participant Policies
    for s in participant_shares:
        p = s.policy
        if p.id not in seen_ids:
            results.append({
                "id": p.id,
                "policy_number": p.policy_number,
                "lead_company": p.company.name,
                "is_lead": False,
                "my_share": float(s.share_percentage),
                "status": p.status,
                "premium_amount": float(p.premium_amount),
                "start_date": p.start_date,
                "end_date": p.end_date
            })
            seen_ids.add(p.id)
            
    return results
