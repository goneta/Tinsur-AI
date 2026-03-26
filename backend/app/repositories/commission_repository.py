"""
Repository for commission operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.commission import Commission


class CommissionRepository:
    """Repository for commission data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, commission: Commission) -> Commission:
        """Create a new commission record."""
        self.db.add(commission)
        self.db.commit()
        self.db.refresh(commission)
        return commission
    
    def get_by_id(self, commission_id: UUID) -> Optional[Commission]:
        """Get commission by ID."""
        return self.db.query(Commission).filter(Commission.id == commission_id).first()
    
    def get_by_company(
        self,
        company_id: UUID,
        agent_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Commission], int]:
        """Get commissions by company with filters."""
        query = self.db.query(Commission).filter(Commission.company_id == company_id)
        
        if agent_id:
            query = query.filter(Commission.agent_id == agent_id)
        if status:
            query = query.filter(Commission.status == status)
        
        total = query.count()
        commissions = query.order_by(Commission.created_at.desc()).offset(skip).limit(limit).all()
        
        return commissions, total
    
    def get_by_policy(self, policy_id: UUID) -> List[Commission]:
        """Get commissions for a specific policy."""
        return self.db.query(Commission).filter(Commission.policy_id == policy_id).all()
    
    def update(self, commission: Commission) -> Commission:
        """Update a commission record."""
        self.db.commit()
        self.db.refresh(commission)
        return commission
