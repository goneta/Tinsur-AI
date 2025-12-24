"""
API endpoints for Telematics.
"""
from typing import List, Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import dependencies as deps
from app.schemas import telematics as schemas
from app.services.telematics_service import TelematicsService

router = APIRouter()

@router.post("/trip/{policy_id}", response_model=schemas.TelematicsData)
def submit_trip_data(
    policy_id: UUID,
    trip_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Submit new telematics trip data for a policy.
    """
    service = TelematicsService(db)
    return service.process_trip_data(policy_id, trip_data)

@router.get("/score/{policy_id}")
def get_safety_score(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Get the current safety score and UBI adjustment for a policy.
    """
    service = TelematicsService(db)
    score = service.calculate_safety_score(policy_id)
    adjustment = service.get_ubi_adjustment(policy_id)
    
    return {
        "policy_id": policy_id,
        "safety_score": float(score),
        "ubi_adjustment_percent": float(adjustment * 100),
        "rating": "excellent" if score > 80 else "good" if score > 60 else "average" if score > 40 else "poor"
    }

@router.get("/history/{policy_id}", response_model=List[schemas.TelematicsData])
def get_trip_history(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
    limit: int = 30
):
    """
    Get recent trip history for a policy.
    """
    from app.models.telematics import TelematicsData
    return db.query(TelematicsData).filter(TelematicsData.policy_id == policy_id).order_by(TelematicsData.trip_date.desc()).limit(limit).all()
