"""
API endpoints for financial reports.
"""
from typing import Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.payment_repository import PaymentRepository
from app.repositories.premium_schedule_repository import PremiumScheduleRepository

router = APIRouter()


@router.get("/revenue/summary")
def get_revenue_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get revenue summary for a date range."""
    payment_repo = PaymentRepository(db)
    
    # Default to current month if no dates provided
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    summary = payment_repo.get_revenue_summary(
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        **summary
    }


@router.get("/revenue/daily")
def get_daily_revenue(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily revenue for the last N days."""
    payment_repo = PaymentRepository(db)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get revenue by day
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        summary = payment_repo.get_revenue_summary(
            company_id=current_user.company_id,
            start_date=current_date,
            end_date=current_date
        )
        
        daily_data.append({
            "date": current_date.isoformat(),
            "revenue": summary['total_revenue'],
            "payments_count": summary['total_payments']
        })
        
        current_date += timedelta(days=1)
    
    return {
        "period": f"Last {days} days",
        "data": daily_data
    }


@router.get("/revenue/monthly")
def get_monthly_revenue(
    months: int = Query(default=12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly revenue for the last N months."""
    payment_repo = PaymentRepository(db)
    
    monthly_data = []
    today = date.today()
    
    for i in range(months):
        # Calculate month start and end
        if i == 0:
            month_end = today
            month_start = today.replace(day=1)
        else:
            month_end = (today.replace(day=1) - timedelta(days=1))
            month_start = month_end.replace(day=1)
            today = month_end
        
        summary = payment_repo.get_revenue_summary(
            company_id=current_user.company_id,
            start_date=month_start,
            end_date=month_end
        )
        
        monthly_data.insert(0, {
            "month": month_start.strftime("%Y-%m"),
            "revenue": summary['total_revenue'],
            "payments_count": summary['total_payments']
        })
    
    return {
        "period": f"Last {months} months",
        "data": monthly_data
    }


@router.get("/premiums/outstanding")
def get_outstanding_premiums(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get outstanding premium summary."""
    schedule_repo = PremiumScheduleRepository(db)
    
    # Get all overdue schedules
    overdue = schedule_repo.get_overdue(current_user.company_id)
    
    # Get upcoming due (next 7 days)
    upcoming = schedule_repo.get_upcoming_due(current_user.company_id, days=7)
    
    overdue_total = sum(s.amount + s.late_fee for s in overdue)
    upcoming_total = sum(s.amount for s in upcoming)
    
    return {
        "overdue": {
            "count": len(overdue),
            "total_amount": float(overdue_total)
        },
        "upcoming_7_days": {
            "count": len(upcoming),
            "total_amount": float(upcoming_total)
        },
        "total_outstanding": float(overdue_total + upcoming_total)
    }


@router.get("/payments/breakdown")
def get_payment_breakdown(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment breakdown by method."""
    payment_repo = PaymentRepository(db)
    
    # Default to current month
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    breakdown = payment_repo.get_payment_breakdown(
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "breakdown": breakdown
    }


@router.get("/dashboard")
def get_financial_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive financial dashboard data."""
    payment_repo = PaymentRepository(db)
    schedule_repo = PremiumScheduleRepository(db)
    
    # Current month revenue
    month_start = date.today().replace(day=1)
    month_end = date.today()
    
    monthly_revenue = payment_repo.get_revenue_summary(
        company_id=current_user.company_id,
        start_date=month_start,
        end_date=month_end
    )
    
    # Today's revenue
    today_revenue = payment_repo.get_revenue_summary(
        company_id=current_user.company_id,
        start_date=date.today(),
        end_date=date.today()
    )
    
    # Outstanding premiums
    overdue = schedule_repo.get_overdue(current_user.company_id)
    upcoming = schedule_repo.get_upcoming_due(current_user.company_id, days=7)
    
    overdue_total = sum(s.amount + s.late_fee for s in overdue)
    upcoming_total = sum(s.amount for s in upcoming)
    
    # Payment breakdown
    payment_breakdown = payment_repo.get_payment_breakdown(
        company_id=current_user.company_id,
        start_date=month_start,
        end_date=month_end
    )
    
    return {
        "today": {
            "revenue": today_revenue['total_revenue'],
            "payments_count": today_revenue['total_payments']
        },
        "current_month": {
            "revenue": monthly_revenue['total_revenue'],
            "payments_count": monthly_revenue['total_payments']
        },
        "outstanding": {
            "overdue_count": len(overdue),
            "overdue_amount": float(overdue_total),
            "upcoming_count": len(upcoming),
            "upcoming_amount": float(upcoming_total)
        },
        "payment_methods": payment_breakdown
    }
