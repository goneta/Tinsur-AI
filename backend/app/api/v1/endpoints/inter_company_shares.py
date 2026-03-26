from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core import dependencies as deps
from app.models.inter_company_share import InterCompanyShare
from app.schemas import inter_company_share as schemas

router = APIRouter()

@router.post("/", response_model=schemas.InterCompanyShare)
def create_share(
    *,
    db: Session = Depends(deps.get_db),
    share_in: schemas.InterCompanyShareCreate,
    current_user = Depends(deps.get_current_active_user),
):
    """
    Share a resource with another company.
    """
    share = InterCompanyShare(
        from_company_id=current_user.company_id,
        to_company_id=share_in.to_company_id,
        resource_type=share_in.resource_type,
        resource_id=share_in.resource_id,
        access_level=share_in.access_level,
        expires_at=share_in.expires_at,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share

@router.get("/", response_model=List[schemas.InterCompanyShare])
def read_shares(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve shares sent or received by the current company.
    """
    # Simple logic: show shares where company is sender OR receiver
    shares = db.query(InterCompanyShare).filter(
        (InterCompanyShare.from_company_id == current_user.company_id) | 
        (InterCompanyShare.to_company_id == current_user.company_id)
    ).offset(skip).limit(limit).all()
    
    # Manually populate names if not using lazy-loaded properties in schema
    for s in shares:
        s.from_company_name = s.from_company.name if s.from_company else "Unknown"
        s.to_company_name = s.to_company.name if s.to_company else "Unknown"
        
    return shares
