from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.quote_element import QuoteElement
from app.models.user import User
from pydantic import BaseModel, condecimal

router = APIRouter()

# Pydantic Models
class QuoteElementBase(BaseModel):
    category: str
    name: str
    value: float
    description: Optional[str] = None
    is_active: bool = True

class QuoteElementCreate(QuoteElementBase):
    pass

class QuoteElementUpdate(QuoteElementBase):
    pass

class QuoteElementOut(QuoteElementBase):
    id: Any
    company_id: Any
    created_at: Any
    updated_at: Any

    class Config:
        orm_mode = True

@router.get("/", response_model=List[QuoteElementOut])
def read_quote_elements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    active_only: bool = False
) -> Any:
    """
    Retrieve quote elements.
    """
    query = db.query(QuoteElement).filter(QuoteElement.company_id == current_user.company_id)
    
    if category:
        query = query.filter(QuoteElement.category == category)
        
    if active_only:
        query = query.filter(QuoteElement.is_active == True)
        
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=QuoteElementOut)
def create_quote_element(
    *,
    db: Session = Depends(get_db),
    quote_element_in: QuoteElementCreate,
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Create new quote element.
    """
    quote_element = QuoteElement(
        **quote_element_in.dict(),
        company_id=current_user.company_id
    )
    db.add(quote_element)
    db.commit()
    db.refresh(quote_element)
    return quote_element

@router.put("/{id}", response_model=QuoteElementOut)
def update_quote_element(
    *,
    db: Session = Depends(get_db),
    id: str,
    quote_element_in: QuoteElementUpdate,
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Update a quote element.
    """
    quote_element = db.query(QuoteElement).filter(
        QuoteElement.id == id,
        QuoteElement.company_id == current_user.company_id
    ).first()
    
    if not quote_element:
        raise HTTPException(status_code=404, detail="Quote element not found")
        
    for field, value in quote_element_in.dict(exclude_unset=True).items():
        setattr(quote_element, field, value)
        
    db.add(quote_element)
    db.commit()
    db.refresh(quote_element)
    return quote_element

@router.delete("/{id}", response_model=QuoteElementOut)
def delete_quote_element(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Delete a quote element.
    """
    quote_element = db.query(QuoteElement).filter(
        QuoteElement.id == id,
        QuoteElement.company_id == current_user.company_id
    ).first()
    
    if not quote_element:
        raise HTTPException(status_code=404, detail="Quote element not found")
        
    db.delete(quote_element)
    db.commit()
    return quote_element
