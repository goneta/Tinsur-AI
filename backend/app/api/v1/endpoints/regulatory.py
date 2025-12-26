"""
Regulatory API endpoints for IFRS 17 and Solvency II.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.regulatory import IFRS17Group, RegulatoryMetricSnapshot
from app.models.user import User
from app.services.regulatory_service import RegulatoryService

router = APIRouter()

class IFRS17GroupCreate(BaseModel):
    name: str
    initial_csm: Decimal
    risk_adjustment: Decimal = Decimal("0.0")
    cohort_year: str
    portfolio: str
    profitability_category: str

@router.get("/solvency/dashboard")
def get_solvency_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "company_admin", "manager", "accountant"]))
):
    """Get real-time Solvency II metrics."""
    service = RegulatoryService(db)
    return service.calculate_solvency_ratio(current_user.company_id)

@router.get("/solvency/history")
def get_solvency_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get history of solvency snapshots."""
    snapshots = db.query(RegulatoryMetricSnapshot).filter(
        RegulatoryMetricSnapshot.company_id == current_user.company_id
    ).order_by(RegulatoryMetricSnapshot.snapshot_date.desc()).limit(30).all()
    return snapshots

@router.post("/ifrs17/groups", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_ifrs17_group(
    group_data: IFRS17GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "company_admin", "accountant"]))
):
    """Create a new IFRS 17 contract group for CSM tracking."""
    group = IFRS17Group(
        company_id=current_user.company_id,
        remaining_csm=group_data.initial_csm,
        **group_data.dict()
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return {"status": "success", "group_id": str(group.id)}

@router.get("/ifrs17/groups")
def get_ifrs17_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all IFRS 17 groups for the company."""
    return db.query(IFRS17Group).filter(IFRS17Group.company_id == current_user.company_id).all()

@router.post("/ifrs17/groups/{group_id}/amortize")
def amortize_csm(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["accountant", "company_admin"]))
):
    """Trigger periodic CSM amortization for a group."""
    service = RegulatoryService(db)
    released = service.amortize_csm(group_id)
    return {"status": "success", "released_amount": float(released or 0)}
