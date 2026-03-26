from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core import dependencies as deps
from app.models.pos_location import POSLocation
from app.models.pos_inventory import POSInventory
from app.schemas.pos_location import POSLocationCreate, POSLocationUpdate, POSLocation as POSLocationSchema
from app.schemas.pos_inventory import POSInventoryCreate, POSInventoryUpdate, POSInventory as POSInventorySchema
from app.schemas.pos_inventory import POSInventoryCreate, POSInventoryUpdate, POSInventory as POSInventorySchema
from app.models.user import User
from app.models.policy import Policy
from app.models.quote import Quote
from sqlalchemy import func
from app.schemas.user import UserResponse as UserSchema

router = APIRouter()


@router.get("/locations", response_model=List[POSLocationSchema])
def get_pos_locations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retrieve all POS locations for the company."""
    return db.query(POSLocation).filter(POSLocation.company_id == current_user.company_id).all()


@router.post("/locations", response_model=POSLocationSchema)
def create_pos_location(
    location_in: POSLocationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new POS location."""
    db_location = POSLocation(
        **location_in.model_dump(),
        company_id=current_user.company_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@router.get("/locations/{location_id}", response_model=POSLocationSchema)
def get_pos_location(
    location_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific POS location."""
    location = db.query(POSLocation).filter(
        POSLocation.id == location_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="POS location not found")
    return location


@router.put("/locations/{location_id}", response_model=POSLocationSchema)
def update_pos_location(
    location_id: UUID,
    location_in: POSLocationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a POS location."""
    db_location = db.query(POSLocation).filter(
        POSLocation.id == location_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="POS location not found")
    
    update_data = location_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)
    
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


# Inventory Endpoints

@router.get("/inventory/{location_id}", response_model=List[POSInventorySchema])
def get_pos_inventory(
    location_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get inventory for a specific POS location."""
    # Verify location belongs to company
    location = db.query(POSLocation).filter(
        POSLocation.id == location_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="POS location not found")
        
    return db.query(POSInventory).filter(POSInventory.pos_location_id == location_id).all()


@router.post("/inventory", response_model=POSInventorySchema)
def create_pos_inventory_item(
    inventory_in: POSInventoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Add a new inventory item to a POS."""
    # Verify location belongs to company
    location = db.query(POSLocation).filter(
        POSLocation.id == inventory_in.pos_location_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="POS location not found")

    db_item = POSInventory(
        **inventory_in.model_dump()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/inventory/{item_id}", response_model=POSInventorySchema)
def update_pos_inventory_item(
    item_id: UUID,
    inventory_in: POSInventoryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update an inventory item."""
    db_item = db.query(POSInventory).join(POSLocation).filter(
        POSInventory.id == item_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = inventory_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Management Endpoints

@router.get("/locations/{location_id}/agents", response_model=List[UserSchema])
def get_pos_agents(
    location_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """List agents assigned to this POS location."""
    # Verify location
    location = db.query(POSLocation).filter(
        POSLocation.id == location_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="POS location not found")
        
    return db.query(User).filter(User.pos_location_id == location_id).all()


@router.get("/locations/{location_id}/stats")
def get_pos_stats(
    location_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get statistics for this POS location."""
    # Verify location
    location = db.query(POSLocation).filter(
        POSLocation.id == location_id,
        POSLocation.company_id == current_user.company_id
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="POS location not found")
        
    # Stats
    active_agents = db.query(User).filter(
        User.pos_location_id == location_id, 
        User.is_active == True
    ).count()
    
    total_policies = db.query(Policy).filter(
        Policy.pos_location_id == location_id,
        Policy.status == 'active'
    ).count()
    
    total_premium = db.query(func.sum(Policy.premium_amount)).filter(
        Policy.pos_location_id == location_id,
        Policy.status == 'active'
    ).scalar() or 0
    
    total_quotes = db.query(Quote).filter(
        Quote.pos_location_id == location_id
    ).count()
    
    return {
        "location_id": str(location_id),
        "location_name": location.name,
        "active_agents": active_agents,
        "total_policies_sold": total_policies,
        "total_premium_collected": float(total_premium),
        "total_quotes_generated": total_quotes
    }
