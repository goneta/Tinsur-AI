"""
API endpoints for Claim Recovery management (Subrogation/Salvage).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.services.recovery_service import RecoveryService

router = APIRouter()

class RecoveryCreate(BaseModel):
    claim_id: UUID
    recovery_type: str # 'subrogation', 'salvage'
    estimated_amount: Decimal
    notes: Optional[str] = None

class RecoveryFinalize(BaseModel):
    actual_recovered_amount: Decimal
    recovery_costs: Decimal = Decimal("0.0")

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_recovery(
    data: RecoveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "company_admin", "manager"]))
):
    """Initiate a new subrogation or salvage recovery case."""
    service = RecoveryService(db)
    try:
        recovery = service.create_recovery_record(
            claim_id=data.claim_id,
            recovery_type=data.recovery_type,
            estimated_amount=data.estimated_amount,
            notes=data.notes
        )
        return {"status": "success", "recovery_id": str(recovery.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pending")
def get_pending_recoveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all open recovery cases for the company."""
    service = RecoveryService(db)
    return service.get_pending_recoveries(current_user.company_id)

@router.post("/{recovery_id}/finalize")
def finalize_recovery(
    recovery_id: UUID,
    data: RecoveryFinalize,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["super_admin", "company_admin", "manager", "accountant"]))
):
    """Record recovery collection and close the case."""
    service = RecoveryService(db)
    try:
        recovery = service.finalize_recovery(
            recovery_id=recovery_id,
            recovered_amount=data.actual_recovered_amount,
            costs=data.recovery_costs
        )
        return {"status": "success", "actual_recovered": float(recovery.actual_recovered_amount)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
