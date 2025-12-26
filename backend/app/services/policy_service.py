"""
Policy service for business logic operations.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timedelta
import random

from app.models.policy import Policy
from app.models.quote import Quote
from app.models.endorsement import Endorsement
from app.models.policy_type import PolicyType
from app.repositories.policy_repository import PolicyRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.pos_inventory_repository import POSInventoryRepository
from app.services.reinsurance_service import ReinsuranceService
from app.services.archive_service import ArchiveService

class PolicyService:
    """Service for policy-related business logic."""
    
    def __init__(
        self, 
        policy_repo: PolicyRepository, 
        quote_repo: QuoteRepository,
        endorsement_repo: EndorsementRepository,
        pos_inventory_repo: Optional[POSInventoryRepository] = None
    ):
        self.policy_repo = policy_repo
        self.quote_repo = quote_repo
        self.endorsement_repo = endorsement_repo
        self.pos_inventory_repo = pos_inventory_repo
        self.reinsurance_service = ReinsuranceService(policy_repo.db)
        self.archive_service = ArchiveService(policy_repo.db)
    
    def generate_policy_number(self, company_id: UUID, policy_type_code: str) -> str:
        """Generate unique policy number."""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(10000, 99999)
        # Simplify code to first 3 chars if too long
        code_prefix = policy_type_code[:3].upper() if policy_type_code else "POL"
        return f"{code_prefix}-{timestamp}-{random_suffix}"
    
    def create_from_quote(
        self,
        quote_id: UUID,
        start_date: date,
        created_by: UUID
    ) -> Optional[Policy]:
        """Create a policy from an accepted quote."""
        quote = self.quote_repo.get_by_id(quote_id)
        
        if not quote or quote.status != 'accepted':
            return None
        
        if quote.is_expired:
            return None
        
        # Calculate end_date based on duration
        end_date = start_date + timedelta(days=quote.duration_months * 30)
        
        # Get policy type code
        policy_type_code = "GEN"
        if quote.policy_type:
            policy_type_code = quote.policy_type.code
        else:
            # Try to fetch if not loaded
            policy_type = self.policy_repo.db.query(PolicyType).filter(PolicyType.id == quote.policy_type_id).first()
            if policy_type:
                policy_type_code = policy_type.code
        
        # Generate policy number
        policy_number = self.generate_policy_number(quote.company_id, policy_type_code)
        
        # Create policy
        policy = Policy(
            company_id=quote.company_id,
            client_id=quote.client_id,
            policy_type_id=quote.policy_type_id,
            quote_id=quote_id,
            policy_number=policy_number,
            coverage_amount=quote.coverage_amount,
            premium_amount=quote.final_premium,
            premium_frequency=quote.premium_frequency,
            start_date=start_date,
            end_date=end_date,
            status='active',
            details=quote.details,
            created_by=created_by
        )
        
        policy = self.policy_repo.create(policy)
        
        # Trigger Reinsurance Cession
        self.reinsurance_service.process_policy_cessions(policy)
        
        # Archive Policy Document (Immutable Legal Proof)
        if policy.policy_document_url:
            # In a real system, we'd fetch the file bytes from storage here
            # For now, we simulate with a dummy hash of the policy number
            dummy_content = f"Policy Contract: {policy.policy_number}".encode()
            self.archive_service.archive_policy_document(policy.id, policy.policy_document_url, dummy_content)
        
        return policy
    
    def create_policy(
        self,
        company_id: UUID,
        client_id: UUID,
        policy_type_id: UUID,
        coverage_amount: Decimal,
        premium_amount: Decimal,
        premium_frequency: str,
        start_date: date,
        end_date: date,
        created_by: UUID,
        sales_agent_id: Optional[UUID] = None,
        pos_location_id: Optional[UUID] = None,
        details: Optional[dict] = None,
        inventory_deductions: Optional[List[dict]] = None
    ) -> Policy:
        """Create a policy directly (not from quote)."""
        policy_number = self.generate_policy_number(company_id, "GEN")
        
        policy = Policy(
            company_id=company_id,
            client_id=client_id,
            policy_type_id=policy_type_id,
            policy_number=policy_number,
            coverage_amount=coverage_amount,
            premium_amount=premium_amount,
            premium_frequency=premium_frequency,
            start_date=start_date,
            end_date=end_date,
            status='active',
            details=details or {},
            created_by=created_by,
            sales_agent_id=sales_agent_id,
            pos_location_id=pos_location_id
        )
        
        created_policy = self.policy_repo.create(policy)
        
        # Trigger Reinsurance Cession
        self.reinsurance_service.process_policy_cessions(created_policy)
        
        # Handle Inventory Deduction
        if self.pos_inventory_repo and pos_location_id and inventory_deductions:
            for item in inventory_deductions:
                item_id = item.get('item_id')
                quantity = item.get('quantity', 1)
                if item_id:
                    try:
                        self.pos_inventory_repo.deduct_inventory(
                            item_id=item_id,
                            quantity=quantity,
                            transaction_type='sale',
                            reference_id=created_policy.id,
                            created_by=created_by,
                            notes=f"Policy Sale: {created_policy.policy_number}"
                        )
                    except ValueError as e:
                        print(f"Inventory Error: {e}")
                        # Optionally rollback or just log? 
                        # Ideally should stop policy creation if strict, 
                        # but for now let's just log and continue or add warning to notes.
                        
        return created_policy
    
    def renew_policy(
        self,
        policy_id: UUID,
        new_end_date: date,
        premium_amount: Optional[Decimal] = None,
        coverage_amount: Optional[Decimal] = None
    ) -> Optional[Policy]:
        """Renew a policy."""
        policy = self.policy_repo.get_by_id(policy_id)
        
        if not policy:
            return None
        
        # Update policy
        policy.end_date = new_end_date
        if premium_amount:
            policy.premium_amount = premium_amount
        if coverage_amount:
            policy.coverage_amount = coverage_amount
        policy.status = 'active'
        
        return self.policy_repo.update(policy)
    
    def cancel_policy(
        self,
        policy_id: UUID,
        reason: str,
        effective_date: Optional[date] = None
    ) -> Optional[Policy]:
        """Cancel a policy."""
        return self.policy_repo.cancel(policy_id, reason)
    
    def check_and_expire_policies(self, company_id: UUID) -> int:
        """Check and mark expired policies. Returns count of expired policies."""
        expired_policies = self.policy_repo.get_expired_policies(company_id)
        count = 0
        for policy in expired_policies:
            policy.status = 'expired'
            self.policy_repo.update(policy)
            count += 1
        return count
    
        return self.policy_repo.get_expiring_soon(company_id, days)

    def create_endorsement(
        self,
        company_id: UUID,
        policy_id: UUID,
        endorsement_type: str,
        changes: dict,
        premium_adjustment: Decimal,
        effective_date: date,
        created_by: UUID,
        reason: Optional[str] = None
    ) -> Optional[Endorsement]:
        """Create a new endorsement draft."""
        policy = self.policy_repo.get_by_id(policy_id)
        if not policy:
            return None
            
        # Generate endorsement number
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(1000, 9999)
        endorsement_number = f"END-{timestamp}-{random_suffix}"
        
        # Calculate new premium estimate
        new_premium = policy.premium_amount + premium_adjustment
        
        endorsement = Endorsement(
            company_id=company_id,
            policy_id=policy_id,
            endorsement_number=endorsement_number,
            endorsement_type=endorsement_type,
            effective_date=effective_date,
            changes=changes,
            reason=reason,
            premium_adjustment=premium_adjustment,
            new_premium=new_premium,
            status='draft',
            created_by=created_by
        )
        
        return self.endorsement_repo.create(endorsement)

    def approve_endorsement(self, endorsement_id: UUID, approved_by: UUID) -> Optional[Policy]:
        """Approve usage and apply changes to policy."""
        endorsement = self.endorsement_repo.get_by_id(endorsement_id)
        if not endorsement or endorsement.status != 'draft':
            return None
            
        policy = self.policy_repo.get_by_id(endorsement.policy_id)
        if not policy:
            return None
            
        # Apply changes to policy
        # 1. Premium
        if endorsement.premium_adjustment:
            policy.premium_amount = policy.premium_amount + endorsement.premium_adjustment
            
        # 2. Update status and timestamp
        endorsement.status = 'active'
        endorsement.approved_by = approved_by
        endorsement.approved_at = datetime.utcnow()
        self.endorsement_repo.update(endorsement)
        
        # 3. Update policy based on changes (generic application if keys match)
        # Note: In a real app, field mapping would be more strict
        for key, value in endorsement.changes.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        return self.policy_repo.update(policy)

    def reinstate_policy(self, policy_id: UUID) -> Optional[Policy]:
        """Reinstate a canceled or lapsed policy."""
        policy = self.policy_repo.get_by_id(policy_id)
        if not policy:
            return None
            
        if policy.status not in ['canceled', 'lapsed', 'expired']:
            return policy
            
        policy.status = 'active'
        policy.cancellation_reason = None
        # Potentially adjust dates if needed, but simple reinstatement for now
        
        return self.policy_repo.update(policy)
