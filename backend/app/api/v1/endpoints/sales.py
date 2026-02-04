"""
Sales endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_agent
from app.models.sales import SalesTransaction, SalesTarget
from app.models.user import User
from app.schemas.sales import (
    SalesTransactionCreate,
    SalesTransactionResponse,
    SalesTargetCreate,
    SalesTargetResponse,
)

router = APIRouter()


@router.post("/transactions", response_model=SalesTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_sales_transaction(
    payload: SalesTransactionCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Record a sales transaction."""
    payload.company_id = current_user.company_id
    transaction = SalesTransaction(
        company_id=payload.company_id,
        policy_id=payload.policy_id,
        employee_id=payload.employee_id,
        pos_location_id=payload.pos_location_id,
        channel=payload.channel,
        sale_amount=payload.sale_amount,
        commission_amount=payload.commission_amount,
        sale_date=payload.sale_date,
        sale_time=payload.sale_time,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/transactions", response_model=List[SalesTransactionResponse])
def list_sales_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    channel: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List sales transactions for the current company."""
    query = db.query(SalesTransaction).filter(SalesTransaction.company_id == current_user.company_id)
    if channel:
        query = query.filter(SalesTransaction.channel == channel)
    if start_date:
        query = query.filter(SalesTransaction.created_at >= start_date)
    if end_date:
        query = query.filter(SalesTransaction.created_at <= end_date)
    return query.order_by(SalesTransaction.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/targets", response_model=SalesTargetResponse, status_code=status.HTTP_201_CREATED)
def create_sales_target(
    payload: SalesTargetCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Create a sales target for an employee."""
    target = SalesTarget(
        employee_id=payload.employee_id,
        period=payload.period,
        target_amount=payload.target_amount,
        target_count=payload.target_count,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


@router.get("/targets", response_model=List[SalesTargetResponse])
def list_sales_targets(
    employee_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List sales targets."""
    query = db.query(SalesTarget)
    if employee_id:
        query = query.filter(SalesTarget.employee_id == employee_id)
    return query.order_by(SalesTarget.created_at.desc()).all()
