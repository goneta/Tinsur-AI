"""
Regulatory service for IFRS 17 and Solvency II calculations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from app.models.regulatory import IFRS17Group, RegulatoryMetricSnapshot
from app.models.ledger import Account, LedgerEntry, JournalEntry
from app.models.policy import Policy
from app.models.claim import Claim

class RegulatoryService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_solvency_ratio(self, company_id: UUID) -> Dict[str, Any]:
        """
        Calculate the real-time Solvency Ratio (Solvency II).
        Formula: Eligible Own Funds / Solvency Capital Requirement (SCR)
        Note: This uses a simplified standard formula for real-time monitoring.
        """
        # 1. Available Capital (Own Funds)
        # Using Total Equity as a proxy for Own Funds
        equity_accounts = self.db.query(Account).filter(
            Account.company_id == company_id,
            Account.account_type == "Equity"
        ).all()
        
        own_funds = Decimal("0.0")
        for acc in equity_accounts:
            balance = self.db.query(
                func.sum(LedgerEntry.credit) - func.sum(LedgerEntry.debit)
            ).filter(LedgerEntry.account_id == acc.id).scalar()
            own_funds += Decimal(str(balance or 0))

        # 2. Solvency Capital Requirement (SCR) - Simplified
        # In a real system, this is a complex aggregation of Market, Credit, and Underwriting risks.
        # Simplified: SCR = (Active Exposure * 10%) + (Unpaid Claims reserve * 20%)
        
        # Underwriting Exposure
        total_exposure = self.db.query(func.sum(Policy.coverage_amount)).filter(
            Policy.company_id == company_id,
            Policy.status == 'active'
        ).scalar() or 0
        underwriting_risk = Decimal(str(total_exposure)) * Decimal("0.10") # 10% risk margin
        
        # Reserve Risk
        pending_claims_sum = self.db.query(func.sum(Claim.claim_amount)).filter(
            Claim.company_id == company_id,
            Claim.status.in_(['submitted', 'under_review'])
        ).scalar() or 0
        reserve_risk = Decimal(str(pending_claims_sum)) * Decimal("0.20") # 20% volatility buffer
        
        # Operational Risk (Fixed flat rate on premiums)
        total_premiums = self.db.query(func.sum(Policy.premium_amount)).filter(
            Policy.company_id == company_id,
            Policy.status == 'active'
        ).scalar() or 0
        operational_risk = Decimal(str(total_premiums)) * Decimal("0.05") # 5% of premium
        
        scr = underwriting_risk + reserve_risk + operational_risk
        
        solvency_ratio = own_funds / scr if scr > 0 else Decimal("0.0")
        
        # Create Snapshot
        snapshot = RegulatoryMetricSnapshot(
            company_id=company_id,
            eligible_own_funds=own_funds,
            scr_amount=scr,
            solvency_ratio=solvency_ratio,
            underwriting_risk_scr=underwriting_risk,
            operational_risk_scr=operational_risk,
            details={
                "exposure": float(total_exposure),
                "reserves": float(pending_claims_sum),
                "ytd_premiums": float(total_premiums)
            }
        )
        self.db.add(snapshot)
        self.db.commit()
        
        return {
            "solvency_ratio": float(solvency_ratio),
            "own_funds": float(own_funds),
            "scr": float(scr),
            "status": "Healthy" if solvency_ratio >= 1.5 else "Watch" if solvency_ratio >= 1.0 else "Critical"
        }

    def amortize_csm(self, group_id: UUID):
        """
        IFRS 17 logic: Partially release the CSM (unearned profit) into revenue as time passes.
        """
        group = self.db.query(IFRS17Group).get(group_id)
        if not group or group.remaining_csm <= 0:
            return
            
        # Simplified release (e.g., straight line 1/12th every month)
        release_amount = group.initial_csm / Decimal("12.0")
        if release_amount > group.remaining_csm:
            release_amount = group.remaining_csm
            
        group.remaining_csm -= release_amount
        
        # In a full system, this would trigger a Journal Entry:
        # DB: Insurance Liability (CSM)
        # CR: Insurance Service Revenue
        
        self.db.commit()
        return release_amount

    def get_csm_projections(self, company_id: UUID) -> List[Dict[str, Any]]:
        """
        Calculates projected CSM revenue release for the next 12 months.
        Aggregates projections from all active IFRS 17 groups.
        """
        groups = self.db.query(IFRS17Group).filter(
            IFRS17Group.company_id == company_id,
            IFRS17Group.status == 'active'
        ).all()
        
        projections = []
        # Current month index (0 to 11 for the next year)
        for i in range(12):
            month_release = Decimal("0.0")
            for group in groups:
                # Basic projection based on straight-line release
                # release = initial_csm / 12
                # We check if remaining CSM is enough for this month's release
                # Simple model: if (i * single_release) < remaining_csm
                single_release = group.initial_csm / Decimal("12.0")
                if (i * single_release) < group.remaining_csm:
                    month_release += single_release
            
            projections.append({
                "month_index": i,
                "projected_release": float(month_release)
            })
            
        return projections
