"""
Repository for policy operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime, date, timedelta

from app.models.policy import Policy


class PolicyRepository:
    """Repository for policy data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, policy: Policy) -> Policy:
        """Create a new policy."""
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def get_by_id(self, policy_id: UUID) -> Optional[Policy]:
        """Get policy by ID."""
        return self.db.query(Policy).filter(Policy.id == policy_id).options(joinedload(Policy.client), joinedload(Policy.creator)).first()
    
    def get_by_quote_id(self, quote_id: UUID) -> Optional[Policy]:
        """Get policy by Quote ID."""
        return self.db.query(Policy).filter(Policy.quote_id == quote_id).first()
    
    def get_by_number(self, policy_number: str) -> Optional[Policy]:
        """Get policy by policy number."""
        return self.db.query(Policy).filter(Policy.policy_number == policy_number).first()
    
    def get_by_company(
        self,
        company_id: UUID,
        client_id: Optional[UUID] = None,
        policy_type_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Policy], int]:
        """Get policies by company with filters."""
        query = self.db.query(Policy).filter(Policy.company_id == company_id).options(joinedload(Policy.client), joinedload(Policy.creator))
        
        if client_id:
            query = query.filter(Policy.client_id == client_id)
        if policy_type_id:
            query = query.filter(Policy.policy_type_id == policy_type_id)
        if status:
            query = query.filter(Policy.status == status)
        
        total = query.count()
        policies = query.order_by(Policy.created_at.desc()).offset(skip).limit(limit).all()
        
        return policies, total
    
    def get_by_client(self, client_id: UUID, skip: int = 0, limit: int = 50) -> tuple[List[Policy], int]:
        """Get policies by client."""
        query = self.db.query(Policy).filter(Policy.client_id == client_id)
        total = query.count()
        policies = query.order_by(Policy.created_at.desc()).offset(skip).limit(limit).all()
        return policies, total
    
    def get_active_policies(self, company_id: UUID) -> List[Policy]:
        """Get all active policies."""
        today = date.today()
        return self.db.query(Policy).filter(
            and_(
                Policy.company_id == company_id,
                Policy.status == 'active',
                Policy.start_date <= today,
                Policy.end_date >= today
            )
        ).all()
    
    def get_expiring_soon(self, company_id: UUID, days: int = 30) -> List[Policy]:
        """Get policies expiring within specified days."""
        today = date.today()
        expiry_date = today + timedelta(days=days)
        return self.db.query(Policy).filter(
            and_(
                Policy.company_id == company_id,
                Policy.status == 'active',
                Policy.end_date >= today,
                Policy.end_date <= expiry_date
            )
        ).all()
    
    def get_expired_policies(self, company_id: UUID) -> List[Policy]:
        """Get expired policies that need status update."""
        today = date.today()
        return self.db.query(Policy).filter(
            and_(
                Policy.company_id == company_id,
                Policy.status == 'active',
                Policy.end_date < today
            )
        ).all()
    
    def update(self, policy: Policy) -> Policy:
        """Update a policy."""
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def cancel(self, policy_id: UUID, reason: str) -> Optional[Policy]:
        """Cancel a policy."""
        policy = self.get_by_id(policy_id)
        if policy:
            policy.status = 'canceled'
            policy.cancellation_reason = reason
            return self.update(policy)
        return None
    
    def search(self, company_id: UUID, search_term: str, skip: int = 0, limit: int = 50) -> tuple[List[Policy], int]:
        """Search policies by policy number or notes."""
        query = self.db.query(Policy).filter(
            and_(
                Policy.company_id == company_id,
                or_(
                    Policy.policy_number.ilike(f'%{search_term}%'),
                    Policy.notes.ilike(f'%{search_term}%')
                )
            )
        )
        total = query.count()
        policies = query.order_by(Policy.created_at.desc()).offset(skip).limit(limit).all()
        return policies, total
