"""
Client repository for database operations.
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.models.client import Client, client_company
from app.schemas.client import ClientCreate, ClientUpdate


class ClientRepository:
    """Client repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, client_data: ClientCreate, user_id: Optional[uuid.UUID] = None) -> Client:
        """Create a new client and link to company.
        
        Args:
            client_data: Client creation data (includes company_id)
            user_id: User ID to link the client to (required for self-registration)
        """
        # Exclude fields that don't belong to Client table
        # company_id is now used for the junction table, not direct column
        exclude_fields = {'password', 'company_id', 'automobile_details'}
        client_dict = client_data.dict(exclude=exclude_fields, exclude_unset=True)
        
        # Set user_id if provided
        if user_id:
            client_dict['user_id'] = user_id
            
        client = Client(**client_dict)
        self.db.add(client)
        
        # Link to company if provided
        if client_data.company_id:
            # We use the junction table directly or via relationship
            # Link via relationship is cleaner
            from app.models.company import Company
            company = self.db.query(Company).filter(Company.id == client_data.company_id).first()
            if company:
                client.companies.append(company)
        
        self.db.flush()
        self.db.refresh(client)
        return client
    
    def get_by_id(self, client_id: uuid.UUID, company_id: Optional[uuid.UUID]) -> Optional[Client]:
        """Get client by ID (with company isolation via junction table)."""
        query = self.db.query(Client).options(
            joinedload(Client.drivers)
        )
        
        if company_id:
            query = query.join(Client.companies).filter(
                Client.id == client_id,
                client_company.c.company_id == company_id
            )
        else:
            query = query.filter(Client.id == client_id)
            
        return query.first()
    
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
            query = query.join(Client.companies).filter(client_company.c.company_id == company_id)
        
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
    
    def count(self, company_id: Optional[uuid.UUID], status: Optional[str] = None) -> int:
        """Count clients for a company."""
        query = self.db.query(Client)
        if company_id:
            query = query.join(Client.companies).filter(client_company.c.company_id == company_id)
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
        
        self.db.flush()
        self.db.refresh(client)
        return client
    
    def delete(self, client_id: uuid.UUID, company_id: uuid.UUID) -> bool:
        """Delete a client."""
        client = self.get_by_id(client_id, company_id)
        if not client:
            return False
        
        self.db.delete(client)
        self.db.flush()
        return True
