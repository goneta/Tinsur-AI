"""
Client endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_agent, get_current_active_user
from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse, 
    ClientAutomobileUpdate, ClientHousingUpdate, ClientHealthUpdate, ClientLifeUpdate
)
from app.repositories.client_repository import ClientRepository
from app.models.client_details import ClientAutomobile, ClientHousing, ClientHealth, ClientLife
from app.models.client import Client
from app.models.user import User
from app.core.agent_client import AgentClient
import json

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Create a new client."""
    # Ensure client is created for the user's company
    client_data.company_id = current_user.company_id
    if not client_data.created_by:
        client_data.created_by = current_user.id
    
    repo = ClientRepository(db)
    client = repo.create(client_data)
    
    # Compliance & AML Agent Screening for Onboarding
    try:
        agent_client = AgentClient()
        screening_payload = {
            "context": "ONBOARDING",
            "first_name": client.first_name,
            "last_name": client.last_name,
            "business_name": client.business_name,
            "email": client.email,
            "phone": client.phone,
            "client_type": client.client_type,
            "country": client.country
        }
        
        response = await agent_client.send_message(
            "compliance_aml_agent",
            json.dumps(screening_payload),
            context={"company_id": str(current_user.company_id)}
        )
        
        if "messages" in response and response["messages"]:
            last_msg = response["messages"][-1]
            compliance_data = json.loads(last_msg["text"])
            
            client.compliance_status = compliance_data.get("status", "flagged")
            client.is_high_risk = compliance_data.get("is_high_risk", False)
            client.compliance_notes = compliance_data.get("notes", "No notes provided.")
            
            # If flagged, change status to suspended or similar
            if client.compliance_status == "flagged" or client.is_high_risk:
                client.status = "suspended"
                print(f"Client {client.id} SUSPENDED for compliance review.")
            
            db.commit()
            db.refresh(client)
    except Exception as e:
        print(f"Client Compliance Agent Error: {str(e)}")
        client.compliance_status = "error"
        client.compliance_notes = f"Failed to run onboarding compliance check: {str(e)}"
        db.commit()

    return client


@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all clients with pagination and filters."""
    repo = ClientRepository(db)
    clients = repo.get_all(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        status=status,
        search=search
    )
    return clients


@router.get("/count")
async def count_clients(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total count of clients."""
    repo = ClientRepository(db)
    count = repo.count(company_id=current_user.company_id, status=status)
    return {"count": count}


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific client by ID."""
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id, current_user.company_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    client_data: ClientUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Update a client."""
    repo = ClientRepository(db)
    client = repo.update(client_id, current_user.company_id, client_data)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Delete a client."""
    repo = ClientRepository(db)
    success = repo.delete(client_id, current_user.company_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return None

# --- Detail Endpoints ---

@router.put("/{client_id}/automobile")
async def update_automobile_details(
    client_id: uuid.UUID,
    details: ClientAutomobileUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Update client automobile details."""
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id, current_user.company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    auto_details = db.query(ClientAutomobile).filter(ClientAutomobile.client_id == client_id).first()
    if not auto_details:
        auto_details = ClientAutomobile(client_id=client_id)
        db.add(auto_details)
    
    for field, value in details.dict(exclude_unset=True).items():
        setattr(auto_details, field, value)
        
    db.commit()
    db.refresh(client) # Refresh client to load relationship
    return {"status": "success", "data": client.automobile_details}


@router.put("/{client_id}/housing")
async def update_housing_details(
    client_id: uuid.UUID,
    details: ClientHousingUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Update client housing details."""
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id, current_user.company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    housing_details = db.query(ClientHousing).filter(ClientHousing.client_id == client_id).first()
    if not housing_details:
        housing_details = ClientHousing(client_id=client_id)
        db.add(housing_details)
    
    for field, value in details.dict(exclude_unset=True).items():
        setattr(housing_details, field, value)
        
    db.commit()
    db.refresh(client)
    return {"status": "success", "data": client.housing_details}


@router.put("/{client_id}/health")
async def update_health_details(
    client_id: uuid.UUID,
    details: ClientHealthUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Update client health details."""
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id, current_user.company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    health_details = db.query(ClientHealth).filter(ClientHealth.client_id == client_id).first()
    if not health_details:
        health_details = ClientHealth(client_id=client_id)
        db.add(health_details)
    
    for field, value in details.dict(exclude_unset=True).items():
        setattr(health_details, field, value)
        
    db.commit()
    db.refresh(client)
    return {"status": "success", "data": client.health_details}


@router.put("/{client_id}/life")
async def update_life_details(
    client_id: uuid.UUID,
    details: ClientLifeUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Update client life insurance details."""
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id, current_user.company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    life_details = db.query(ClientLife).filter(ClientLife.client_id == client_id).first()
    if not life_details:
        life_details = ClientLife(client_id=client_id)
        db.add(life_details)
    
    for field, value in details.dict(exclude_unset=True).items():
        setattr(life_details, field, value)
        
    db.commit()
    db.refresh(client)
    return {"status": "success", "data": client.life_details}

# Uploads Configuration
# clients.py is in backend/app/api/v1/endpoints/
# We want backend/uploads/clients
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "clients")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/{client_id}/profile-picture", response_model=ClientResponse)
def upload_client_profile_picture(
    client_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a profile picture for a client.
    """
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id, current_user.company_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"client_{client_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update client record
        relative_path = f"/uploads/clients/{filename}"
        
        # Use repository or direct DB update. Repository update expects schema.
        # Direct update is simpler for single field.
        client.profile_picture = relative_path
        db.commit()
        db.refresh(client)
        return client
        
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Could not save profile picture: {str(e)}")
