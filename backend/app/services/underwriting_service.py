"""
Underwriting service for managing authority and referrals.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import joinedload

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

    def create_referral(
        self, 
        referred_by_id: UUID, 
        reason: str,
        quote_id: Optional[UUID] = None, 
        endorsement_id: Optional[UUID] = None
    ) -> UnderwritingReferral:
        """
        Create a new underwriting referral for a quote or endorsement.
        """
        if not quote_id and not endorsement_id:
            raise ValueError("Either quote_id or endorsement_id must be provided")
            
        company_id = None
        if quote_id:
            from app.models.quote import Quote
            quote = self.db.query(Quote).get(quote_id)
            if not quote:
                raise ValueError("Quote not found")
            company_id = quote.company_id
            quote.status = 'referred'
        elif endorsement_id:
            from app.models.endorsement import Endorsement
            endorsement = self.db.query(Endorsement).get(endorsement_id)
            if not endorsement:
                raise ValueError("Endorsement not found")
            company_id = endorsement.company_id
            endorsement.status = 'pending_approval'
            
        referral = UnderwritingReferral(
            company_id=company_id,
            quote_id=quote_id,
            endorsement_id=endorsement_id,
            referred_by_id=referred_by_id,
            reason=reason,
            status='pending'
        )
        self.db.add(referral)
        self.db.commit()
        return referral

    def process_referral_decision(self, referral_id: UUID, decided_by_id: UUID, status: str, notes: str) -> Optional[Any]:
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
        
        result = None
        # Update quote status
        if referral.quote_id:
            quote = self.db.query(Quote).get(referral.quote_id)
            if quote:
                if status == 'approved':
                    quote.status = 'accepted'
                else:
                    quote.status = 'rejected'
                result = quote
        
        # Update endorsement status
        elif referral.endorsement_id:
            from app.models.endorsement import Endorsement
            endorsement = self.db.query(Endorsement).get(referral.endorsement_id)
            if endorsement:
                if status == 'approved':
                    endorsement.status = 'approved'
                    endorsement.approved_by = decided_by_id
                    endorsement.approved_at = datetime.utcnow()
                else:
                    endorsement.status = 'rejected'
                    endorsement.rejection_reason = notes
                result = endorsement
            
        self.db.commit()
        return result

    def get_pending_referrals(self, company_id: UUID) -> List[UnderwritingReferral]:
        """Get all pending referrals for a company."""
        return self.db.query(UnderwritingReferral).options(
            joinedload(UnderwritingReferral.quote).joinedload(Quote.client),
            joinedload(UnderwritingReferral.referrer)
        ).filter(
            UnderwritingReferral.company_id == company_id,
            UnderwritingReferral.status == 'pending'
        ).all()
