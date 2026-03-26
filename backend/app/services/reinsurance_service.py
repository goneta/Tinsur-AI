"""
Reinsurance service for managing treaties, cessions and recoveries.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import List, Optional
from datetime import date

from app.models.reinsurance import ReinsuranceTreaty, ReinsuranceCession, ReinsuranceRecovery
from app.models.policy import Policy
from app.models.claim import Claim

class ReinsuranceService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_treaties(self, company_id: UUID, policy_type_id: Optional[UUID] = None) -> List[ReinsuranceTreaty]:
        """Fetch active treaties for a company and optionally filter by policy type."""
        query = self.db.query(ReinsuranceTreaty).filter(
            ReinsuranceTreaty.company_id == company_id,
            ReinsuranceTreaty.status == 'active',
            ReinsuranceTreaty.start_date <= date.today(),
            ReinsuranceTreaty.end_date >= date.today()
        )
        
        # If policy_type_id is provided, include treaties with that type OR null (global)
        if policy_type_id:
            query = query.filter(
                (ReinsuranceTreaty.policy_type_id == policy_type_id) | 
                (ReinsuranceTreaty.policy_type_id == None)
            )
        else:
            query = query.filter(ReinsuranceTreaty.policy_type_id == None)
            
        return query.all()

    def process_policy_cessions(self, policy: Policy):
        """Calculate and record premium cessions based on active treaties."""
        treaties = self.get_active_treaties(policy.company_id, policy.policy_type_id)
        
        for treaty in treaties:
            if treaty.treaty_type == 'quota_share':
                # Proportional Sharing
                share_decimal = treaty.share_percentage / 100
                ceded_premium = Decimal(str(policy.premium_amount)) * share_decimal
                commission = ceded_premium * (treaty.commission_percentage / 100)
                net_to_reinsurer = ceded_premium - commission
                
                cession = ReinsuranceCession(
                    company_id=policy.company_id,
                    policy_id=policy.id,
                    treaty_id=treaty.id,
                    gross_premium=policy.premium_amount,
                    ceded_premium=ceded_premium,
                    reinsurance_commission=commission,
                    net_to_reinsurer=net_to_reinsurer
                )
                self.db.add(cession)
        
        self.db.commit()

    def process_claim_recovery(self, claim: Claim):
        """Calculate and record claim recoverables from reinsurers."""
        # Find active treaties at the time the claim is approved
        # This usually follows the policy's tied treaties
        cessions = self.db.query(ReinsuranceCession).filter(ReinsuranceCession.policy_id == claim.policy_id).all()
        
        approved_amount = Decimal(str(claim.approved_amount or claim.claim_amount))
        
        for cession in cessions:
            treaty = self.db.query(ReinsuranceTreaty).get(cession.treaty_id)
            if not treaty or treaty.treaty_type != 'quota_share':
                continue
                
            share_decimal = treaty.share_percentage / 100
            recoverable_amount = approved_amount * share_decimal
            
            recovery = ReinsuranceRecovery(
                company_id=claim.company_id,
                claim_id=claim.id,
                treaty_id=treaty.id,
                gross_claim_amount=approved_amount,
                recoverable_amount=recoverable_amount
            )
            self.db.add(recovery)
            
        self.db.commit()
