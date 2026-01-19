"""
Client repository for database operations.
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


class ClientRepository:
    """Client repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, client_data: ClientCreate) -> Client:
        """Create a new client."""
        client = Client(**client_data.dict())
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client
    
    def get_by_id(self, client_id: uuid.UUID, company_id: uuid.UUID) -> Optional[Client]:
        """Get client by ID (with company isolation)."""
        return self.db.query(Client).options(
            joinedload(Client.drivers)
        ).filter(
            Client.id == client_id,
            Client.company_id == company_id
        ).first()
    
    def get_all(
        self,
        company_id: Optional[uuid.UUID],
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Client]:
        """Get all clients with pagination and filters. If company_id is None, return all (Admin/Public)."""
        query = self.db.query(Client)
        if company_id:
            query = query.filter(Client.company_id == company_id)
        
        if status:
            query = query.filter(Client.status == status)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Client.first_name.ilike(search_filter)) |
                (Client.last_name.ilike(search_filter)) |
                (Client.business_name.ilike(search_filter)) |
                (Client.email.ilike(search_filter)) |
                (Client.phone.ilike(search_filter))
            )
        
        return query.order_by(Client.updated_at.desc()).offset(skip).limit(limit).all()
    
    def count(self, company_id: uuid.UUID, status: Optional[str] = None) -> int:
        """Count clients for a company."""
        query = self.db.query(Client).filter(Client.company_id == company_id)
        if status:
            query = query.filter(Client.status == status)
        return query.count()
    
    def update(
        self,
        client_id: uuid.UUID,
        company_id: uuid.UUID,
        client_data: ClientUpdate
    ) -> Optional[Client]:
        """Update a client."""
        client = self.get_by_id(client_id, company_id)
        if not client:
            return None
        
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        self.db.commit()
        self.db.refresh(client)
        return client
    
    def delete(self, client_id: uuid.UUID, company_id: uuid.UUID) -> bool:
        """Delete a client."""
        client = self.get_by_id(client_id, company_id)
        if not client:
            return False
        
        self.db.delete(client)
        self.db.commit()
        return True
