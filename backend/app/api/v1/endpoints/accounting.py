"""
Accounting API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.accounting_service import AccountingService
from app.schemas.ledger import AccountResponse, JournalEntryResponse, TrialBalanceItem

router = APIRouter()

@router.get("/accounts", response_model=List[AccountResponse])
def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve chart of accounts."""
    from app.models.ledger import Account
    return db.query(Account).filter(Account.company_id == current_user.company_id).all()

@router.get("/ledger", response_model=List[JournalEntryResponse])
def get_ledger(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve ledger journal entries."""
    service = AccountingService(db)
    return service.get_ledger_history(current_user.company_id, limit=limit)

@router.get("/trial-balance", response_model=List[TrialBalanceItem])
def get_trial_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve trial balance report."""
    service = AccountingService(db)
    return service.get_trial_balance(current_user.company_id)

@router.post("/initialize")
def initialize_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize default chart of accounts for the company."""
    if current_user.role not in ['admin', 'super_admin', 'company_admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    service = AccountingService(db)
    service.initialize_chart_of_accounts(current_user.company_id)
    return {"status": "success", "message": "Chart of accounts initialized"}
