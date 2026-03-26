"""
Referral Service for managing client referrals.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import uuid
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.referral import Referral

class ReferralService:
    """Service for handling referrals."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def create_referral(self, company_id: UUID, referrer_client_id: UUID) -> Referral:
        """
        Generates a new unique referral code for a client.
        Checks if one already exists for this company/client pair.
        """
        # Check if already has a code in this company
        existing = self.db.query(Referral).filter(
            Referral.company_id == company_id,
            Referral.referrer_client_id == referrer_client_id
        ).first()
        
        if existing:
            return existing
            
        # Generate random code
        # Using a loop to ensure uniqueness, though collision is unlikely with random 8 chars
        while True:
            code_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            new_code = f"REF-{code_suffix}"
            
            # Check if code exists globally (or just handle integrity error, but check is nicer)
            code_check = self.db.query(Referral).filter(Referral.referral_code == new_code).first()
            if not code_check:
                break
        
        new_referral = Referral(
            company_id=company_id,
            referrer_client_id=referrer_client_id,
            referral_code=new_code,
            status='pending',
            reward_amount=5000.0, # Default reward, could be configurable later
            reward_paid=False
        )
        self.db.add(new_referral)
        self.db.commit()
        self.db.refresh(new_referral)
        
        return new_referral

    def get_client_referrals(self, company_id: UUID, client_id: UUID) -> List[Referral]:
        """Get all referrals initiated by a specific client in a company."""
        return self.db.query(Referral).filter(
            Referral.company_id == company_id,
            Referral.referrer_client_id == client_id
        ).all()

    def get_company_stats(self, company_id: UUID) -> Dict[str, Any]:
        """Get company-wide referral statistics."""
        total_rewards = self.db.query(func.sum(Referral.reward_amount)).filter(
            Referral.company_id == company_id,
            Referral.reward_paid == True
        ).scalar() or 0
        
        pending_conversions = self.db.query(Referral).filter(
            Referral.company_id == company_id,
            Referral.status == "pending"
        ).count()

        converted_count = self.db.query(Referral).filter(
            Referral.company_id == company_id,
            Referral.status == "converted"
        ).count()
        
        return {
            "total_rewards": total_rewards,
            "pending_conversions": pending_conversions,
            "converted_count": converted_count
        }

    def get_referral_by_code(self, code: str) -> Optional[Referral]:
        """Retrieve a referral by its code."""
        return self.db.query(Referral).filter(Referral.referral_code == code).first()
