"""
Repository for claim operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date

from app.models.claim import Claim

class ClaimRepository:
    """Repository for claim data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, claim: Claim) -> Claim:
        """Create a new claim."""
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        return claim
    
    def get_by_id(self, claim_id: UUID) -> Optional[Claim]:
        """Get claim by ID."""
        return self.db.query(Claim).filter(Claim.id == claim_id).first()
    
    def get_by_number(self, claim_number: str) -> Optional[Claim]:
        """Get claim by claim number."""
        return self.db.query(Claim).filter(Claim.claim_number == claim_number).first()
    
    def get_all(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        policy_id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        adjuster_id: Optional[UUID] = None
    ) -> tuple[List[Claim], int]:
        """Get claims with filters."""
        query = self.db.query(Claim).filter(Claim.company_id == company_id)
        
        if status:
            query = query.filter(Claim.status == status)
        if policy_id:
            query = query.filter(Claim.policy_id == policy_id)
        if client_id:
            query = query.filter(Claim.client_id == client_id)
        if adjuster_id:
            query = query.filter(Claim.adjuster_id == adjuster_id)
            
        total = query.count()
        claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
        
        return claims, total
    
    def update(self, claim: Claim) -> Claim:
        """Update a claim."""
        self.db.commit()
        self.db.refresh(claim)
        return claim
    
    def delete(self, claim_id: UUID) -> bool:
        """Delete a claim."""
        claim = self.get_by_id(claim_id)
        if claim:
            self.db.delete(claim)
            self.db.commit()
            return True
        return False
