"""
Accounting API endpoints.
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.services.accounting_service import AccountingService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from datetime import date, datetime, timedelta
from app.services.accounting_service import AccountingService
from app.schemas.ledger import (
    AccountResponse, 
    JournalEntryResponse, 
    TrialBalanceItem,
    ProfitLossResponse,
    BalanceSheetResponse
)

router = APIRouter()

# ... existing endpoints (get_accounts, get_ledger, get_trial_balance, initialize_accounts) ...

@router.get("/profit-loss", response_model=ProfitLossResponse)
def get_profit_loss(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve Profit and Loss report."""
    service = AccountingService(db)
    
    # Defaults
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date.replace(month=1, day=1) # YTD
        
    # Convert date to datetime for service
    s_dt = datetime.combine(start_date, datetime.min.time())
    e_dt = datetime.combine(end_date, datetime.max.time())
    
    return service.get_profit_loss(current_user.company_id, s_dt, e_dt)

@router.get("/balance-sheet", response_model=BalanceSheetResponse)
def get_balance_sheet(
    as_of_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve Balance Sheet report."""
    service = AccountingService(db)
    
    if not as_of_date:
        as_of_date = date.today()
        
    ao_dt = datetime.combine(as_of_date, datetime.max.time())
    
    return service.get_balance_sheet(current_user.company_id, ao_dt)

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
