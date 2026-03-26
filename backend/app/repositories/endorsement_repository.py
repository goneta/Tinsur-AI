"""
Repository for endorsement operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.endorsement import Endorsement


class EndorsementRepository:
    """Repository for endorsement data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, endorsement: Endorsement) -> Endorsement:
        """Create a new endorsement."""
        self.db.add(endorsement)
        self.db.commit()
        self.db.refresh(endorsement)
        return endorsement
    
    def get_by_id(self, endorsement_id: UUID) -> Optional[Endorsement]:
        """Get endorsement by ID."""
        return self.db.query(Endorsement).filter(Endorsement.id == endorsement_id).first()
    
    def get_by_number(self, endorsement_number: str) -> Optional[Endorsement]:
        """Get endorsement by endorsement number."""
        return self.db.query(Endorsement).filter(Endorsement.endorsement_number == endorsement_number).first()
    
    def get_by_policy(self, policy_id: UUID, skip: int = 0, limit: int = 50) -> tuple[List[Endorsement], int]:
        """Get endorsements for a policy."""
        query = self.db.query(Endorsement).filter(Endorsement.policy_id == policy_id)
        total = query.count()
        endorsements = query.order_by(Endorsement.created_at.desc()).offset(skip).limit(limit).all()
        return endorsements, total
    
    def update(self, endorsement: Endorsement) -> Endorsement:
        """Update an endorsement."""
        self.db.commit()
        self.db.refresh(endorsement)
        return endorsement
    
    def delete(self, endorsement_id: UUID) -> bool:
        """Delete an endorsement."""
        endorsement = self.get_by_id(endorsement_id)
        if endorsement:
            self.db.delete(endorsement)
            self.db.commit()
            return True
        return False
