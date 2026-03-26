from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core import dependencies as deps
from app.models.ml_model import MLModel
from app.schemas import ml_model as schemas

from app.services.ml_service import MLService

router = APIRouter()

@router.get("/", response_model=List[schemas.MLModel])
def read_ml_models(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    List deployed ML models.
    """
    models = db.query(MLModel).offset(skip).limit(limit).all()
    return models

@router.post("/predict/churn/{client_id}")
def predict_churn(
    client_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Predict churn risk for a client.
    """
    service = MLService(db)
    return service.predict_churn(client_id)

@router.post("/predict/fraud/{claim_id}")
def predict_fraud(
    claim_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Predict fraud risk for a claim.
    """
    service = MLService(db)
    return service.predict_fraud(claim_id)
