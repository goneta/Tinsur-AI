from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core import dependencies as deps
from app.models.company import Company
from app.schemas.company import CompanyResponse as CompanySchema
from app.schemas.company import CompanyUpdate

router = APIRouter()

@router.get("/", response_model=List[CompanySchema])
def read_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve companies (public metadata).
    Used for B2B sharing. Excludes current user's company.
    """
    # Exclude own company
    query = db.query(Company).filter(Company.id != current_user.company_id)
    
    # Filter by search term
    if search:
        search_filter = or_(
            Company.name.ilike(f"%{search}%"),
            Company.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
        
    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/me", response_model=CompanySchema)
def read_own_company(
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's company details.
    """
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/me", response_model=CompanySchema)
def update_own_company(
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user's company.
    """
    deps.require_admin(current_user)
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
        
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
