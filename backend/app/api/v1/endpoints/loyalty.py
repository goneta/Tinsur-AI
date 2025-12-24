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
