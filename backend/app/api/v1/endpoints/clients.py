"""
Client endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_agent, get_current_active_user, get_optional_user

from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse, 
    ClientAutomobileUpdate, ClientHousingUpdate, ClientHealthUpdate, ClientLifeUpdate,
    ClientAutomobileCreate, ClientAutomobileResponse,
    ClientDriverCreate, ClientDriverResponse, ClientDriverUpdate
)
from app.repositories.client_repository import ClientRepository
from app.services.client_service import ClientService
from app.models.client_details import ClientAutomobile, ClientHousing, ClientHealth, ClientLife, ClientDriver
from app.models.client import Client
from app.models.user import User
from app.core.agent_client import AgentClient
import json

router = APIRouter()

@router.get("/me", response_model=ClientResponse)
async def get_current_client(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current client information based on logged in user."""
    client = db.query(Client).options(
        joinedload(Client.drivers),
        joinedload(Client.automobile_details)
    ).filter(Client.user_id == current_user.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client record not found for this user")
    return client

@router.get("/debug-auth")
def debug_auth(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Debug endpoint to check headers and auth state."""
    auth_header = request.headers.get("Authorization", "Missing")
    return {
        "message": "Debug Auth",
        "auth_header_prefix": auth_header[:10] if auth_header else "None",
        "user_found": bool(current_user),
        "user_email": current_user.email if current_user else None,
        "user_role": current_user.role if current_user else None,
        "company_id": str(current_user.company_id) if current_user else None
    }

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Create a new client.
    
    - If authenticated (admin/agent): Create Client for managed client
    - If unauthenticated (self-registration): Create User + Client atomically
    """
    try:
        if current_user:
            # Authenticated flow: admin/agent creating a client
            client_data.company_id = current_user.company_id
            if not client_data.created_by:
                client_data.created_by = current_user.id
            
            service = ClientService(db)
            client = await service.create_client(client_data)
        else:
            # Unauthenticated self-registration flow
            if not client_data.password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password required for client self-registration"
                )
            
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == client_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # 1. & 2. Create User and Client atomically via ClientService
            service = ClientService(db)
            client = await service.register_client(client_data)
            
            # 3. Commit transaction
            db.commit()
            db.refresh(client)
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create client: {str(e)}"
        )
    
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
            context={"company_id": str(current_user.company_id)} if current_user else {}
        )
        
        if "messages" in response and response["messages"]:
            last_msg = response["messages"][-1]
            compliance_data = json.loads(last_msg["text"])
            
            client.compliance_status = compliance_data.get("status", "flagged")
            client.is_high_risk = compliance_data.get("is_high_risk", False)
            client.compliance_notes = compliance_data.get("notes", "No notes provided.")
            
            if client.compliance_status == "flagged" or client.is_high_risk:
                client.status = "suspended"
            
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
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get all clients."""
    repo = ClientRepository(db)
    company_id = current_user.company_id if current_user else None
    
    clients = repo.get_all(
        company_id=company_id,
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
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get a specific client by ID."""
    repo = ClientRepository(db)
    # If unauth, we might restrict this later. For now, allow (demo purposes)
    client = db.query(Client).options(
        joinedload(Client.drivers),
        joinedload(Client.automobile_details)
    ).filter(Client.id == client_id)
    
    if current_user and current_user.company_id:
         # Optionally filter by company if desired
         pass
         
    client = client.first()
    
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
    """Update primary client automobile details."""
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
    db.refresh(client)
    return {"status": "success", "data": client.automobile_details}

@router.put("/{client_id}/vehicles/{vehicle_id}", response_model=ClientAutomobileResponse)
async def update_client_vehicle(
    client_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    vehicle_data: ClientAutomobileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific vehicle."""
    repo = ClientRepository(db)
    
    # Auth Check
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client or client.id != client_id:
             raise HTTPException(status_code=403, detail="Not authorized to update vehicles for this client")
        # For multi-company clients, check if they belong to the current company if needed
        # For now, if it's the client themselves, they have access to their own data
        company_id = None # Repository will handle retrieval by client_id if company_id is None for non-agent
    else:
        # Verify agent has access to this client's company
        company_id = current_user.company_id
        
    client = repo.get_by_id(client_id, company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    vehicle = db.query(ClientAutomobile).filter(
        ClientAutomobile.id == vehicle_id,
        ClientAutomobile.client_id == client_id
    ).first()
    
    if not vehicle:
         raise HTTPException(status_code=404, detail="Vehicle not found")
         
    for field, value in vehicle_data.dict(exclude_unset=True).items():
        setattr(vehicle, field, value)
        
    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.post("/{client_id}/vehicles", response_model=ClientAutomobileResponse)
async def create_client_vehicle(
    client_id: uuid.UUID,
    vehicle_data: ClientAutomobileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new vehicle to the client."""
    repo = ClientRepository(db)
    
    # Auth Check
    if current_user.role == 'client':
        # Verify the user is the client themselves
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client or client.id != client_id:
             raise HTTPException(status_code=403, detail="Not authorized to add vehicles for this client")
        company_id = None
    else:
        # Verify agent has access to this client's company
        company_id = current_user.company_id
        
    client = repo.get_by_id(client_id, company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    vehicle = ClientAutomobile(**vehicle_data.dict(), client_id=client_id)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.post("/{client_id}/drivers", response_model=ClientDriverResponse)
async def create_client_driver(
    client_id: uuid.UUID,
    driver_data: ClientDriverCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new driver to the client."""
    repo = ClientRepository(db)

    # Auth Check
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client or client.id != client_id:
             raise HTTPException(status_code=403, detail="Not authorized to add drivers for this client")
        company_id = None
    else:
        company_id = current_user.company_id

    client = repo.get_by_id(client_id, company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    driver = ClientDriver(**driver_data.dict(), client_id=client_id)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver

@router.put("/{client_id}/drivers/{driver_id}", response_model=ClientDriverResponse)
async def update_client_driver(
    client_id: uuid.UUID,
    driver_id: uuid.UUID,
    driver_data: ClientDriverUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing driver."""
    repo = ClientRepository(db)
    
    # Auth Check
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client or client.id != client_id:
             raise HTTPException(status_code=403, detail="Not authorized to update drivers for this client")
        company_id = None
    else:
        # Verify agent has access to this client's company
        company_id = current_user.company_id
        
    client = repo.get_by_id(client_id, company_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found in company {company_id}")
        
    driver = db.query(ClientDriver).filter(
        ClientDriver.id == driver_id, 
        ClientDriver.client_id == client_id
    ).first()
    
    if not driver:
        # Check if driver exists but for different client to give better error
        driver_any_client = db.query(ClientDriver).filter(ClientDriver.id == driver_id).first()
        if driver_any_client:
            raise HTTPException(status_code=404, detail=f"Driver found but belongs to client {driver_any_client.client_id}, not {client_id}")
        else:
            raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")
    
    for field, value in driver_data.dict(exclude_unset=True).items():
        setattr(driver, field, value)
        
    db.commit()
    db.refresh(driver)
    return driver


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
    # Auth Check
    if current_user.role == 'client':
        if current_user.id != db.query(Client).filter(Client.id == client_id).first().user_id:
             raise HTTPException(status_code=403, detail="Not authorized to update this client")
        company_id = None
    else:
        company_id = current_user.company_id

    client = repo.get_by_id(client_id, company_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"client_{client_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        relative_path = f"/uploads/clients/{filename}"
        client.profile_picture = relative_path
        db.commit()
        db.refresh(client)
        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

@router.post("/{client_id}/drivers/{driver_id}/license", response_model=ClientDriverResponse)
def upload_driver_license(
    client_id: uuid.UUID,
    driver_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a driving license for a driver.
    """
    repo = ClientRepository(db)
    
    # Auth Check
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client or client.id != client_id:
             raise HTTPException(status_code=403, detail="Not authorized to update drivers for this client")
        company_id = None
    else:
        # Verify agent has access to this client's company
        company_id = current_user.company_id
        
    client = repo.get_by_id(client_id, company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    driver = db.query(ClientDriver).filter(
        ClientDriver.id == driver_id, 
        ClientDriver.client_id == client_id
    ).first()
    
    if not driver:
         raise HTTPException(status_code=404, detail="Driver not found")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Ensure upload directory exists
    DRIVER_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "drivers")
    if not os.path.exists(DRIVER_UPLOAD_DIR):
        os.makedirs(DRIVER_UPLOAD_DIR)

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"license_{driver_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(DRIVER_UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        relative_path = f"/uploads/drivers/{filename}"
        driver.driving_license_url = relative_path
        db.commit()
        db.refresh(driver)
        return driver
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

@router.post("/{client_id}/vehicles/{vehicle_id}/image", response_model=ClientAutomobileResponse)
async def upload_vehicle_image(
    client_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a vehicle image for a specific vehicle."""
    repo = ClientRepository(db)
    
    # Auth Check
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client or client.id != client_id:
             raise HTTPException(status_code=403, detail="Not authorized to update vehicles for this client")
    
    automobile = db.query(ClientAutomobile).filter(
        ClientAutomobile.id == vehicle_id,
        ClientAutomobile.client_id == client_id
    ).first()
    
    if not automobile:
        raise HTTPException(status_code=404, detail="Vehicle record not found")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Ensure upload directory exists
    VEHICLE_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "vehicles")
    if not os.path.exists(VEHICLE_UPLOAD_DIR):
        os.makedirs(VEHICLE_UPLOAD_DIR)

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vehicle_{vehicle_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(VEHICLE_UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        relative_path = f"/uploads/vehicles/{filename}"
        automobile.vehicle_image_url = relative_path
        db.commit()
        db.refresh(automobile)
        return automobile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
