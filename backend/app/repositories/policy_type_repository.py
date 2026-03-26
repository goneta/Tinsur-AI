"""
Repository for policy type operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.policy_type import PolicyType


class PolicyTypeRepository:
    """Repository for policy type data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, policy_type: PolicyType) -> PolicyType:
        """Create a new policy type."""
        self.db.add(policy_type)
        self.db.commit()
        self.db.refresh(policy_type)
        return policy_type
    
    def get_by_id(self, policy_type_id: UUID) -> Optional[PolicyType]:
        """Get policy type by ID."""
        return self.db.query(PolicyType).filter(PolicyType.id == policy_type_id).first()
    
    def get_by_code(self, company_id: UUID, code: str) -> Optional[PolicyType]:
        """Get policy type by code."""
        return self.db.query(PolicyType).filter(
            PolicyType.company_id == company_id,
            PolicyType.code == code
        ).first()
    
    def get_by_company(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None
    ) -> tuple[List[PolicyType], int]:
        """Get policy types by company."""
        query = self.db.query(PolicyType).filter(PolicyType.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(PolicyType.is_active == is_active)
            
        total = query.count()
        policy_types = query.order_by(PolicyType.name).offset(skip).limit(limit).all()
        
        return policy_types, total

    def update(self, policy_type: PolicyType) -> PolicyType:
        """Update a policy type."""
        self.db.commit()
        self.db.refresh(policy_type)
        return policy_type
    
    def delete(self, policy_type_id: UUID) -> bool:
        """Delete a policy type."""
        policy_type = self.get_by_id(policy_type_id)
        if policy_type:
            self.db.delete(policy_type)
            self.db.commit()
            return True
        return False
