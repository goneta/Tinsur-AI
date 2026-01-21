
"""
Client Service for managing client lifecycle and related entities.
"""
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime
import json

from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate
from app.models.client import Client
from app.models.user import User
from app.models.client_details import ClientDriver, ClientAutomobile
from app.core.agent_client import AgentClient
from app.core.security import get_password_hash

class ClientService:
    """Service for handling client business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ClientRepository(db)
        
    async def create_client(
        self,
        client_data: ClientCreate,
        user_id: Optional[uuid.UUID] = None,
        context: Optional[dict] = None
    ) -> Client:
        """
        Create a client and automatically generate driver card.
        If user_id is provided, it will be set on the client record.
        """
        # 1. Create the Client Record with user_id
        client = self.repo.create(client_data, user_id=user_id)
            
        # 2. Automatic Driver Card Generation
        if client.client_type == 'individual' or (client.first_name and client.last_name):
            print(f"DEBUG_CLIENT_SERVICE: Triggering _create_automatic_driver for client_id: {client.id}")
            self._create_automatic_driver(client)
        else:
            print(f"DEBUG_CLIENT_SERVICE: Skipping _create_automatic_driver for client_id: {client.id} (type: {client.client_type}, name: {client.first_name} {client.last_name})")
            
        # 3. Create Vehicles if provided
        if client_data.automobile_details:
            print(f"DEBUG_CLIENT_SERVICE: Creating automobiles for client_id: {client.id}")
            self._create_automobiles(client, client_data.automobile_details)

        self.db.flush()
        return client

    async def register_client(self, client_data: ClientCreate) -> Client:
        """
        Consolidated registration: Create User and then Client.
        """
        # 1. Create User record
        user = User(
            email=client_data.email,
            password_hash=get_password_hash(client_data.password),
            first_name=client_data.first_name,
            last_name=client_data.last_name,
            phone=client_data.phone,
            user_type="client",
            company_id=client_data.company_id,
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        self.db.flush()
        
        # 2. Create Client record and related entities
        client = await self.create_client(client_data, user_id=user.id)
        
        self.db.commit()
        return client

    def _create_automatic_driver(self, client: Client) -> None:
        """
        Create a ClientDriver record based on Client details.
        """
        try:
            # Check if driver already exists for this client
            existing_driver = self.db.query(ClientDriver).filter(
                ClientDriver.client_id == client.id,
                ClientDriver.is_main_driver == True
            ).first()

            if existing_driver:
                print(f"DEBUG_CLIENT_SERVICE: Automatic driver already exists for client_id: {client.id}")
                return

            # Map Client fields to Driver fields
            print(f"DEBUG_CLIENT_SERVICE: Mapping fields for automatic driver. Client Name: {client.first_name} {client.last_name}")
            driver = ClientDriver(
                id=uuid.uuid4(),
                client_id=client.id,
                is_main_driver=True,
                first_name=client.first_name,
                last_name=client.last_name,
                phone_number=client.phone,
                address=client.address,
                city=client.city,
                country=client.country,
                license_number=client.driving_licence_number, 
                date_of_birth=client.date_of_birth,
                
                # Initialize defaults
                accident_count=client.accident_count or 0,
                no_claims_years=client.no_claims_years or 0,
                driving_license_years=client.driving_license_years or 0,
                driving_license_url=client.driving_license_url
            )
            
            self.db.add(driver)
            self.db.flush()
            print(f"DEBUG_CLIENT_SERVICE: Successfully created automatic driver for client_id: {client.id}")
        except Exception as e:
            print(f"ERROR_CLIENT_SERVICE: Failed to create automatic driver for client_id: {client.id}. Error: {str(e)}")
            # Don't raise, allowing registration to continue but logging failure

    def _create_automobiles(self, client: Client, vehicles_data: list) -> None:
        """
        Create ClientAutomobile records from provided data.
        """
        try:
            for vehicle_data in vehicles_data:
                vehicle = ClientAutomobile(
                    id=uuid.uuid4(),
                    client_id=client.id,
                    **vehicle_data.dict(exclude_unset=True)
                )
                self.db.add(vehicle)
            self.db.flush()
            print(f"DEBUG_CLIENT_SERVICE: Successfully created {len(vehicles_data)} automobiles for client_id: {client.id}")
        except Exception as e:
            print(f"ERROR_CLIENT_SERVICE: Failed to create automobiles for client_id: {client.id}. Error: {str(e)}")
