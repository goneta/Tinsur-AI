from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
import uuid
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.payroll import PayrollTransaction
from app.models.employee import EmployeeProfile
from app.schemas.employee import PayrollTransactionCreate, PayrollTransactionResponse, PayrollGenerateRequest
from app.services.payroll_service import PayrollService

router = APIRouter()

@router.get("/", response_model=List[PayrollTransactionResponse])
def get_payroll_transactions(
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List payroll transactions.
    """
    stmt = select(PayrollTransaction).where(PayrollTransaction.company_id == current_user.company_id)
    
    if employee_id:
        stmt = stmt.where(PayrollTransaction.employee_id == employee_id)
        
    stmt = stmt.order_by(desc(PayrollTransaction.payment_date)).offset(skip).limit(limit)
    
    transactions = db.execute(stmt).scalars().all()
    
    # Enhance response with employee names
    # (Pydantic model will grab this if configured properly via relationship, or we can manually attach)
    # The PayrollTransaction model has 'employee' relationship, so from_attributes=True in schema should handle it if accessible
    
    return transactions

@router.post("/", response_model=PayrollTransactionResponse)
def create_payroll_transaction(
    transaction_in: PayrollTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a payroll payment.
    """
    # Verify employee exists and belongs to company
    stmt = select(User).where(User.id == transaction_in.employee_id, User.company_id == current_user.company_id)
    employee = db.execute(stmt).scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    new_transaction = PayrollTransaction(
        employee_id=transaction_in.employee_id,
        company_id=current_user.company_id,
        amount=transaction_in.amount,
        currency=transaction_in.currency,
        payment_method=transaction_in.payment_method,
        status='paid', # Assuming immediate recording of payment
        description=transaction_in.description,
        payment_month=transaction_in.payment_month,
        reference_number=transaction_in.reference_number,
        processed_by=current_user.id,
        payment_date=datetime.utcnow()
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction
@router.post("/generate", response_model=List[PayrollTransactionResponse])
def generate_payroll(
    request: PayrollGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk generate payroll for all employees for a given month.
    """
    if current_user.role not in ['admin', 'manager', 'company_admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Not authorized to generate payroll")
        
    payroll_service = PayrollService(db)
    results = payroll_service.process_monthly_payroll(
        company_id=current_user.company_id,
        month=request.month,
        processor_id=current_user.id
    )
    return results

@router.get("/{id}", response_model=PayrollTransactionResponse)
def get_payroll_transaction(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single payroll transaction by ID.
    """
    stmt = select(PayrollTransaction).where(
        PayrollTransaction.id == id,
        PayrollTransaction.company_id == current_user.company_id
    )
    transaction = db.execute(stmt).scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Payroll transaction not found")
        
    return transaction
