from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID


from app.core.database import get_db
from app.models.policy_service import PolicyService
from app.schemas.policy_service import PolicyServiceCreate, PolicyServiceUpdate, PolicyService as PolicyServiceSchema

router = APIRouter()

@router.get("/", response_model=List[PolicyServiceSchema])
def read_policy_services(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    company_id: UUID = Query(..., description="Company ID to filter by"),
    search: str = Query(None, description="Search by name"),
    is_active: bool = Query(None, description="Filter by active status")
) -> Any:
    """
    Retrieve policy services.
    """
    query = db.query(PolicyService).filter(PolicyService.company_id == company_id)
    
    if search:
        query = query.filter(PolicyService.name_en.ilike(f"%{search}%"))
        
    if is_active is not None:
        query = query.filter(PolicyService.is_active == is_active)
        
    services = query.offset(skip).limit(limit).all()
    return services

@router.post("/", response_model=PolicyServiceSchema)
def create_policy_service(
    *,
    db: Session = Depends(get_db),
    service_in: PolicyServiceCreate,
) -> Any:
    """
    Create new policy service.
    """
    service = PolicyService(
        company_id=service_in.company_id,
        name_en=service_in.name_en,
        name_fr=service_in.name_fr,
        description=service_in.description,
        default_price=service_in.default_price,
        is_active=service_in.is_active
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.put("/{service_id}", response_model=PolicyServiceSchema)
def update_policy_service(
    *,
    db: Session = Depends(get_db),
    service_id: UUID,
    service_in: PolicyServiceUpdate,
) -> Any:
    """
    Update a policy service.
    """
    service = db.query(PolicyService).filter(PolicyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Policy service not found")
        
    update_data = service_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
        
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}", response_model=PolicyServiceSchema)
def delete_policy_service(
    *,
    db: Session = Depends(get_db),
    service_id: UUID,
) -> Any:
    """
    Delete a policy service.
    """
    service = db.query(PolicyService).filter(PolicyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Policy service not found")
        
    db.delete(service)
    db.commit()
    return service
