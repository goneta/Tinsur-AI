"""
Service for claim business logic.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime
import random
import string

from app.models.claim import Claim
from app.models.claim_activity import ClaimActivity
from app.models.policy import Policy
from app.models.co_insurance import CoInsuranceShare
from app.models.inter_company_share import InterCompanyShare
from app.repositories.claim_repository import ClaimRepository
from app.services.reinsurance_service import ReinsuranceService
from app.schemas.claim import ClaimCreate, ClaimUpdate
from app.core.agent_client import AgentClient
from app.models.client import Client
from decimal import Decimal
import json
from app.services.ai_service import AiService
from app.core.time import utcnow
from app.services.production_launch_control_service import ActorContext, ProductionActionControlService

class ClaimService:
    """Service for handling claim operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ClaimRepository(db)
        self.reinsurance_service = ReinsuranceService(db)
        self.ai_service = AiService(db)

    def _add_activity(self, claim_id: UUID, action: str, user_id: Optional[UUID] = None, notes: Optional[str] = None):
        activity = ClaimActivity(
            claim_id=claim_id,
            user_id=user_id,
            action=action,
            notes=notes,
        )
        self.db.add(activity)
        self.db.commit()
        
    def _generate_claim_number(self) -> str:
        """Generate a random claim number."""
        # Format: CLM-YYYYMMDD-XXXX
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"CLM-{date_str}-{random_str}"
        
    def create_claim(self, claim_data: ClaimCreate, actor_roles: Optional[List[str]] = None) -> Claim:
        """Create a new claim."""
        # Verify policy exists
        policy = self.db.query(Policy).get(claim_data.policy_id)
        if not policy:
            raise ValueError("Policy not found")
        
        # Verify policy was active at incident date
        if not (policy.start_date <= claim_data.incident_date <= policy.end_date):
             # Depending on business rules we might reject or just warn. 
             # For now, we will allow creation but maybe flag it? 
             # Let's simple check it belongs to the company
             pass
             
        if policy.company_id != claim_data.company_id:
            raise ValueError("Policy does not belong to this company")

        ProductionActionControlService(self.db).enforce_action(
            action_key="create_claim_record",
            actor=ActorContext(actor_id=claim_data.created_by, company_id=claim_data.company_id, roles=tuple(actor_roles or ())),
            company_id=claim_data.company_id,
            target_type="policy",
            target_id=claim_data.policy_id,
            payload={"claim_amount": str(claim_data.claim_amount), "incident_date": claim_data.incident_date.isoformat()},
        )

        claim_number = self._generate_claim_number()
        
        # Create claim model
        claim = Claim(
            claim_number=claim_number,
            policy_id=claim_data.policy_id,
            client_id=policy.client_id, # Inherit client from policy
            company_id=claim_data.company_id,
            incident_date=claim_data.incident_date,
            incident_description=claim_data.incident_description,
            incident_location=claim_data.incident_location,
            claim_amount=claim_data.claim_amount,
            evidence_files=claim_data.evidence_files,
            status='submitted',
            created_by=claim_data.created_by
        )
        
        created = self.repository.create(claim)
        self._add_activity(created.id, "submitted", claim_data.created_by)
        return created
    
    def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        """Get claim by ID."""
        return self.repository.get_by_id(claim_id)
        
    def get_claims(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> tuple[List[Claim], int]:
        """Get claims for a company."""
        return self.repository.get_all(company_id, skip, limit, status)
        
    async def update_claim(self, claim_id: UUID, update_data: ClaimUpdate, user_id: Optional[UUID] = None, actor_roles: Optional[List[str]] = None, approval_request_id: Optional[UUID] = None, payment_live_mode: Optional[bool] = None) -> Optional[Claim]:
        """Update a claim with mandatory AML screening for payouts."""
        claim = self.repository.get_by_id(claim_id)
        if not claim:
            return None
            
        if update_data.approved_amount is not None:
            claim.approved_amount = update_data.approved_amount
        if update_data.adjuster_id:
            claim.adjuster_id = update_data.adjuster_id
            
        # Update fields if provided
        if update_data.status:
            old_status = claim.status
            new_status = update_data.status
            
            # Launch-control gates and AML screening for payouts
            if new_status in ['approved', 'paid'] and old_status not in ['approved', 'paid']:
                ProductionActionControlService(self.db).enforce_action(
                    action_key="settle_claim" if new_status == "paid" else "approve_claim",
                    actor=ActorContext(actor_id=user_id, company_id=claim.company_id, roles=tuple(actor_roles or ())),
                    company_id=claim.company_id,
                    target_type="claim",
                    target_id=claim_id,
                    payload={"old_status": old_status, "new_status": new_status, "approved_amount": str(update_data.approved_amount or claim.approved_amount or claim.claim_amount)},
                    approval_request_id=approval_request_id,
                    payment_live_mode=payment_live_mode if new_status == "paid" else None,
                )
                try:
                    client = self.db.query(Client).get(claim.client_id)
                    if client:
                        agent_client = AgentClient()
                        payout_payload = {
                            "context": "PAYOUT",
                            "claim_number": claim.claim_number,
                            "claim_amount": str(claim.claim_amount),
                            "approved_amount": str(claim.approved_amount or claim.claim_amount),
                            "first_name": client.first_name,
                            "last_name": client.last_name,
                            "email": client.email,
                            "client_id": str(client.id)
                        }
                        
                        response = await agent_client.send_message(
                            "compliance_aml_agent",
                            json.dumps(payout_payload),
                            context={"company_id": str(claim.company_id)}
                        )
                        
                        if "messages" in response and response["messages"]:
                            last_msg = response["messages"][-1]
                            compliance_data = json.loads(last_msg["text"])
                            
                            # Update client compliance status if it's more restrictive
                            if compliance_data.get("status") == "flagged":
                                client.compliance_status = "flagged"
                                client.is_high_risk = True
                                client.compliance_notes = f"PAYOUT FLAG: {compliance_data.get('notes')}"
                                self.db.commit()
                                
                                # REJECT the payout status change
                                claim.status = "flagged"
                                claim.fraud_details = {
                                    "type": "aml_alert",
                                    "message": "Payout blocked by Compliance Agent.",
                                    "notes": compliance_data.get("notes"),
                                    "at": utcnow().isoformat(),
                                }
                                self.repository.update(claim)
                                return claim
                except Exception as e:
                    # Log and continue (Agent unavailable/error)
                    pass

            claim.status = new_status
            if old_status != new_status:
                self._add_activity(claim.id, f"status_changed:{old_status}->{new_status}", user_id)
            
            # If claim is approved, handle co-insurance settlements and reinsurance recovery
            if claim.status == 'approved' and old_status != 'approved':
                self._generate_co_insurance_settlements(claim)
                self.reinsurance_service.process_claim_recovery(claim)
                
        if update_data.incident_description:
            claim.incident_description = update_data.incident_description
        if update_data.evidence_files is not None:
             claim.evidence_files = update_data.evidence_files
             
        return self.repository.update(claim)

    def _generate_co_insurance_settlements(self, claim: Claim):
        """Generate inter-company settlements for co-insurance participants."""
        # 1. Get co-insurance shares for the policy
        shares = self.db.query(CoInsuranceShare).filter(CoInsuranceShare.policy_id == claim.policy_id).all()
        
        if not shares:
            return

        approved_amount = Decimal(str(claim.approved_amount or claim.claim_amount))
        
        for share in shares:
            # 2. Calculate participant's share of the claim
            settlement_amount = (approved_amount * share.share_percentage) / 100
            
            # 3. Create inter-company settlement entry
            settlement = InterCompanyShare(
                from_company_id=claim.company_id, # Lead insurer (paying)
                to_company_id=share.company_id,   # Participant insurer (reimbursing)
                resource_type="claim_settlement",
                resource_id=claim.id,
                amount=settlement_amount,
                currency="XOF", # Default or from policy
                access_level="read",
                notes=f"Co-insurance share of {share.share_percentage}% for claim {claim.claim_number}. Amount: {settlement_amount}"
            )
            self.db.add(settlement)
        
        self.db.commit()

    async def analyze_claim_damage(self, claim_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Trigger AI analysis for claim evidence photos."""
        claim = self.get_claim(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        
        if not claim.evidence_files:
            return {"error": "No evidence files found for this claim"}
        
        # 1. Run Analysis
        results = await self.ai_service.analyze_damage(str(claim.company_id), claim.evidence_files)
        
        if "error" in results:
            return results
            
        # 2. Update Claim with AI assessment
        claim.ai_assessment = results
        self._add_activity(claim.id, "ai_damage_analysis", user_id)
        
        # 3. Log usage
        self.ai_service.log_and_consume_usage(
            str(claim.company_id), 
            str(user_id), 
            "Damage_Vision_Agent",
            cost=0.50 
        )
        
        self.repository.update(claim)
        
        # 4. Notify Adjuster
        try:
            from app.services.notification_service import NotificationService
            notif_service = NotificationService(self.db)
            notif_service.send_claim_assessment_alert(
                company_id=claim.company_id,
                adjuster_id=user_id,
                claim_number=claim.claim_number,
                severity=results.get('severity'),
                estimate=results.get('suggested_estimate')
            )
        except Exception as e:
            print(f"Failed to send assessment notification: {e}")

        # 5. Automatically Run Fraud Detection
        try:
            await self.ai_service.detect_claim_fraud(claim.id)
            self._add_activity(claim.id, "fraud_scan", user_id)
        except Exception as e:
            print(f"Failed to run automated fraud detection: {e}")

        return results

    async def analyze_claim_fraud(self, claim_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Trigger a standalone fraud analysis for a claim."""
        claim = self.repository.get_by_id(claim_id)
        if not claim:
            return {"error": "Claim not found"}
        
        # Deduct credits for fraud analysis
        self.ai_service.log_and_consume_usage(
            str(claim.company_id), 
            str(user_id), 
            "FraudDetectionAgent", 
            cost=0.1 # Fraud analysis is more expensive
        )
        
        results = await self.ai_service.detect_claim_fraud(claim.id)
        self._add_activity(claim.id, "fraud_scan_manual", user_id)
        return results
