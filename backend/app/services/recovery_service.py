"""
Recovery service for managing subrogation and salvage operations.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.recovery import ClaimRecovery
from app.models.claim import Claim
from app.models.ledger import Account, JournalEntry, LedgerEntry

class RecoveryService:
    def __init__(self, db: Session):
        self.db = db

    def create_recovery_record(
        self, 
        claim_id: UUID, 
        recovery_type: str, 
        estimated_amount: Decimal,
        notes: Optional[str] = None
    ) -> ClaimRecovery:
        """Create a new recovery case (Subrogation or Salvage)."""
        claim = self.db.query(Claim).get(claim_id)
        if not claim:
            raise ValueError("Claim not found")
            
        recovery = ClaimRecovery(
            company_id=claim.company_id,
            claim_id=claim_id,
            recovery_type=recovery_type,
            estimated_amount=estimated_amount,
            status='identified',
            notes=notes
        )
        self.db.add(recovery)
        self.db.commit()
        self.db.refresh(recovery)
        return recovery

    def finalize_recovery(
        self, 
        recovery_id: UUID, 
        recovered_amount: Decimal, 
        costs: Decimal = Decimal("0.0")
    ) -> ClaimRecovery:
        """
        Record the final recovered amount and close the case.
        Triggers accounting entries (simplified).
        """
        recovery = self.db.query(ClaimRecovery).get(recovery_id)
        if not recovery:
            raise ValueError("Recovery record not found")
            
        recovery.actual_recovered_amount = recovered_amount
        recovery.recovery_costs = costs
        recovery.status = 'recovered'
        
        # In a real system, we'd trigger a Journal Entry:
        # DB: Cash/Bank
        # CR: Claim Recovery Income (or reduction in claim expense)
        
        self.db.commit()
        return recovery

    def get_pending_recoveries(self, company_id: UUID) -> List[ClaimRecovery]:
        """Get all open recovery cases."""
        return self.db.query(ClaimRecovery).filter(
            ClaimRecovery.company_id == company_id,
            ClaimRecovery.status.in_(['identified', 'in_progress', 'negotiation'])
        ).all()
