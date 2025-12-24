from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.core import dependencies as deps
from app.models.policy import Policy
from app.models.quote import Quote
from app.models.pos_location import POSLocation
from app.models.user import User
from app.core.database import Base

router = APIRouter()

@router.get("/summary")
def get_sales_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get sales summary (total volume, count) within a date range."""
    query = db.query(Policy).filter(Policy.company_id == current_user.company_id)
    
    if start_date:
        query = query.filter(Policy.created_at >= start_date)
    if end_date:
        query = query.filter(Policy.created_at <= end_date)
        
    total_sales = query.count()
    total_revenue = query.with_entities(func.sum(Policy.premium_amount)).scalar() or 0
    
    return {
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/by-channel")
def get_sales_by_channel(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get sales breakdown by channel."""
    results = db.query(
        Policy.sale_channel,
        func.count(Policy.id).label("count"),
        func.sum(Policy.premium_amount).label("revenue")
    ).filter(
        Policy.company_id == current_user.company_id
    ).group_by(Policy.sale_channel).all()
    
    return [
        {"channel": r.sale_channel, "count": r.count, "revenue": r.revenue or 0}
        for r in results
    ]

@router.get("/by-pos")
def get_sales_by_pos(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get sales performance by POS location."""
    results = db.query(
        POSLocation.name,
        func.count(Policy.id).label("count"),
        func.sum(Policy.premium_amount).label("revenue")
    ).join(
        Policy, Policy.pos_location_id == POSLocation.id
    ).filter(
        Policy.company_id == current_user.company_id
    ).group_by(POSLocation.name).order_by(desc("revenue")).all()
    
    return [
        {"pos_name": r.name, "count": r.count, "revenue": r.revenue or 0}
        for r in results
    ]

@router.get("/leaderboard")
def get_sales_leaderboard(
    limit: int = 10,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get top performing sales agents."""
    # Note: Policy.created_by tracks the user who created the policy
    results = db.query(
        User.first_name,
        User.last_name,
        func.count(Policy.id).label("count"),
        func.sum(Policy.premium_amount).label("revenue")
    ).join(
        Policy, Policy.sales_agent_id == User.id
    ).filter(
        Policy.company_id == current_user.company_id,
        User.role.in_(['agent', 'manager'])
    ).group_by(User.id).order_by(desc("revenue")).limit(limit).all()
    
    return [
        {
            "agent_name": f"{r.first_name} {r.last_name}",
            "count": r.count,
            "revenue": r.revenue or 0
        }
        for r in results
    ]
