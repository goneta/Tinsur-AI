"""
Underwriting service for managing authority and referrals.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.underwriting import UnderwritingReferral
from app.models.user import User
from app.models.quote import Quote

class UnderwritingService:
    def __init__(self, db: Session):
        self.db = db

    def is_within_authority(self, user_id: UUID, coverage_amount: Decimal) -> bool:
        """
        Check if the coverage amount is within the user's underwriting authority.
        Super admins and company admins are assumed to have unlimited authority 
        unless specific limits are set.
        """
        user = self.db.query(User).get(user_id)
        if not user:
            return False
            
        if user.role in ['super_admin', 'company_admin']:
            return True
            
        return coverage_amount <= user.underwriting_limit

    def create_referral(self, quote_id: UUID, referred_by_id: UUID, reason: str) -> UnderwritingReferral:
        """
        Create a new underwriting referral for a quote.
        """
        quote = self.db.query(Quote).get(quote_id)
        if not quote:
            raise ValueError("Quote not found")
            
        referral = UnderwritingReferral(
            company_id=quote.company_id,
            quote_id=quote_id,
            referred_by_id=referred_by_id,
            reason=reason,
            status='pending'
        )
        self.db.add(referral)
        
        # Update quote status to referred
        quote.status = 'referred'
        
        self.db.commit()
        return referral

    def process_referral_decision(self, referral_id: UUID, decided_by_id: UUID, status: str, notes: str) -> Quote:
        """
        Process a decision on an underwriting referral.
        Status must be 'approved' or 'rejected'.
        """
        if status not in ['approved', 'rejected']:
            raise ValueError("Invalid status. Must be 'approved' or 'rejected'.")
            
        referral = self.db.query(UnderwritingReferral).get(referral_id)
        if not referral:
            raise ValueError("Referral not found")
            
        referral.status = status
        referral.decision_notes = notes
        referral.decided_by_id = decided_by_id
        referral.decided_at = datetime.utcnow()
        
        # Update quote status
        quote = self.db.query(Quote).get(referral.quote_id)
        if quote:
            if status == 'approved':
                quote.status = 'accepted' # Or 'draft' depending on workflow, setting 'accepted' to allow issuance
            else:
                quote.status = 'rejected'
        
        self.db.commit()
        return quote

    def get_pending_referrals(self, company_id: UUID) -> List[UnderwritingReferral]:
        """Get all pending referrals for a company."""
        return self.db.query(UnderwritingReferral).filter(
            UnderwritingReferral.company_id == company_id,
            UnderwritingReferral.status == 'pending'
        ).all()
