"""
Commission service for calculating and managing sales commissions.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from app.models.commission import Commission
from app.models.policy import Policy
from app.repositories.commission_repository import CommissionRepository


class CommissionService:
    """Service for handling commission-related business logic."""
    
    def __init__(self, commission_repo: CommissionRepository):
        self.commission_repo = commission_repo
    
    def calculate_and_create_commission(
        self,
        policy: Policy,
        amount: Decimal
    ) -> Optional[Commission]:
        """
        Calculate and create a commission for a policy sale/payment.
        Amount is usually the premium amount paid.
        """
        # Determine the agent to attribute the sale to
        # 1. Check if there's a specific sales_agent_id on the policy
        # 2. Fallback to created_by if it's an agent/manager
        agent_id = policy.sales_agent_id or policy.created_by
        
        if not agent_id:
            return None
            
        # Default commission rate (10%)
        # In production, this would be fetched from agent profile or policy type settings
        commission_rate = Decimal('0.10') 
        commission_amount = amount * commission_rate
        
        commission = Commission(
            company_id=policy.company_id,
            agent_id=agent_id,
            policy_id=policy.id,
            amount=commission_amount,
            status='pending'
        )
        
        return self.commission_repo.create(commission)
    
    def mark_as_paid(self, commission_id: UUID) -> Optional[Commission]:
        """Mark a commission as paid."""
        commission = self.commission_repo.get_by_id(commission_id)
        if not commission:
            return None
            
        commission.status = 'paid'
        commission.paid_at = datetime.utcnow()
        return self.commission_repo.update(commission)
    
    def get_agent_commissions(self, company_id: UUID, agent_id: UUID) -> List[Commission]:
        """Get all commissions for a specific agent."""
        commissions, _ = self.commission_repo.get_by_company(
            company_id=company_id,
            agent_id=agent_id,
            limit=1000
        )
        return commissions
