from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core import dependencies as deps
from app.models.loyalty import LoyaltyPoint
from app.schemas import loyalty as schemas
from app.models.client import Client

from app.services.loyalty_service import LoyaltyService

router = APIRouter()

@router.get("/stats")
def read_loyalty_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Get company-wide loyalty statistics.
    """
    from sqlalchemy import func
    
    total_points = db.query(func.sum(LoyaltyPoint.points_balance)).filter(
        LoyaltyPoint.company_id == current_user.company_id
    ).scalar() or 0
    
    active_members = db.query(LoyaltyPoint).filter(
        LoyaltyPoint.company_id == current_user.company_id
    ).count()
    
    tier_counts = db.query(
        LoyaltyPoint.tier, func.count(LoyaltyPoint.id)
    ).filter(
        LoyaltyPoint.company_id == current_user.company_id
    ).group_by(LoyaltyPoint.tier).all()
    
    # Recent earnings (simplified)
    recent_earnings = db.query(LoyaltyPoint).filter(
        LoyaltyPoint.company_id == current_user.company_id
    ).order_by(LoyaltyPoint.updated_at.desc()).limit(10).all()
    
    return {
        "total_points": total_points,
        "active_members": active_members,
        "tiers": {tier: count for tier, count in tier_counts},
        "recent_activity": [
            {
                "client_id": str(lp.client_id),
                "client_name": f"{lp.client.first_name} {lp.client.last_name}" if lp.client else "Unknown",
                "points": lp.points_balance,
                "tier": lp.tier,
                "updated_at": lp.updated_at.isoformat()
            } for lp in recent_earnings
        ]
    }

@router.get("/{client_id}", response_model=schemas.LoyaltyPoint)
def read_loyalty_points(
    client_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Get loyalty points and tier for a client.
    """
    service = LoyaltyService(db)
    return service.get_or_create_loyalty(client_id)

@router.post("/{client_id}/redeem")
def redeem_loyalty_points(
    client_id: UUID,
    points: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Redeem loyalty points for a discount.
    """
    service = LoyaltyService(db)
    try:
        discount = service.redeem_points(client_id, points)
        return {"discount_amount": discount, "message": f"Successfully redeemed {points} points"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
