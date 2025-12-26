"""
Reinsurance API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.reinsurance import ReinsuranceTreaty, ReinsuranceCession, ReinsuranceRecovery
from app.models.user import User

router = APIRouter()

class TreatyCreate(BaseModel):
    reinsurer_name: str
    treaty_number: str
    share_percentage: Decimal
    commission_percentage: Decimal = Decimal("0.00")
    treaty_type: str = "quota_share"
    policy_type_id: Optional[UUID] = None
    start_date: date
    end_date: date

@router.post("/treaties", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_treaty(
    treaty_data: TreatyCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new reinsurance treaty."""
    treaty = ReinsuranceTreaty(
        company_id=current_user.company_id,
        **treaty_data.dict()
    )
    db.add(treaty)
    db.commit()
    db.refresh(treaty)
    return {"status": "success", "treaty_id": str(treaty.id)}

@router.get("/treaties")
async def get_treaties(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all treaties for the company."""
    treaties = db.query(ReinsuranceTreaty).filter(ReinsuranceTreaty.company_id == current_user.company_id).all()
    return treaties

@router.get("/cessions")
async def get_cessions(
    policy_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all premium cessions."""
    query = db.query(ReinsuranceCession).filter(ReinsuranceCession.company_id == current_user.company_id)
    if policy_id:
        query = query.filter(ReinsuranceCession.policy_id == policy_id)
    return query.all()

@router.get("/recoveries")
async def get_recoveries(
    claim_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all claim recoveries."""
    query = db.query(ReinsuranceRecovery).filter(ReinsuranceRecovery.company_id == current_user.company_id)
    if claim_id:
        query = query.filter(ReinsuranceRecovery.claim_id == claim_id)
    return query.all()
