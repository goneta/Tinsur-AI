from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from models import ClaimRequest, ClaimResponse
import json
import uuid
import re
from datetime import datetime
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.security_context import SecurityService
from app.services.claim_service import ClaimService

class ClaimsAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="claims_agent",
            model="gemini-3-pro-preview",
            description="Agent that processes claims and detects fraud",
            instruction="""
            You are a Claims Agent.
            Analyze claims for fraud.
            """,
        )

    async def _parse_input(self, history: list) -> ClaimRequest:
        """Uses Gemini to extract field values from chat history (Structured Output)."""
        if not history:
            return ClaimRequest()

        history_text = ""
        for h in history:
            role = "User" if h["role"] == "user" else "Assistant"
            text = h["text"]
            history_text += f"{role}: {text}\n"

        extraction_instruction = """
        Analyze the conversation history and extract claim details.
        - Extract the incident description.
        - Extract the amount (estimate) as a float.
        - Extract the policy ID if mentioned.
        - Extract the incident date if mentioned.
        - If a field is not mentioned, keep it as null.
        """

        try:
            extractor = Agent(
                name="claim_extractor",
                model="gemini-3-pro-preview",
                instruction=extraction_instruction,
                output_type=ClaimRequest
            )
            
            extracted = await extractor.run(f"Extract from this history:\n\n{history_text}")
            
            if isinstance(extracted, ClaimRequest):
                return extracted
            elif isinstance(extracted, dict):
                return ClaimRequest(**extracted)
            return ClaimRequest()
        except Exception as e:
            print(f"Claim Extraction Error: {e}. Falling back to empty request.")
            return ClaimRequest()

    def _process_claim(self, request: ClaimRequest) -> ClaimResponse:
        """Fraud Detection Logic."""
        fraud_score = 0
        status = "Approved"
        
        # Rule 1: High Amount
        if request.amount > 5000:
            fraud_score += 30
            
        # Rule 2: Suspicious Keywords
        suspicious_words = ["stolen", "lost", "cash", "unknown"]
        if any(w in request.description.lower() for w in suspicious_words):
            fraud_score += 40
            
        # Rule 3: Policy Check (Mock)
        if request.policy_id == "UNKNOWN":
            fraud_score += 10
            
        if fraud_score > 50:
            status = "Under Review"
            msg = "Claim flagged for manual review due to high risk score."
        else:
            msg = "Claim processed automatically."

        return ClaimResponse(
            claim_id=str(uuid.uuid4())[:8],
            status=status,
            fraud_score=fraud_score,
            message=msg,
            processed_at=datetime.now().isoformat()
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        # Build history from context events OR metadata
        history = context.metadata.get("history", [])
        if not history and context.events:
             for event in context.events:
                 history.append({
                     "role": "user" if event.type == "user_text_message" else "assistant",
                     "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                     "type": event.type
                 })
        
        user_input = history[-1]["text"] if history else ""
        
        try:
            # Security Check
            user_id = context.metadata.get("user_id")
            policy_id_ctx = context.metadata.get("policy_id")

            if not user_id:
                # Debug
                response_text = f"Debug: No user_id found. Metadata keys: {list(context.metadata.keys())}"
                event_queue.enqueue_event(new_agent_text_message(response_text))
                return

            db = SessionLocal()
            try:
                # 1. RBAC Check
                security = SecurityService(db)
                if not security.has_permission(uuid.UUID(user_id), "claim", "write"):
                    response_text = "Permission Denied: You do not have access to file claims."
                    event_queue.enqueue_event(new_agent_text_message(response_text))
                    return

                # 2. Parse Input
                if "share" in user_input.lower() or "settle" in user_input.lower():
                    # Inter-company Settlement Logic
                    from app.models.inter_company_share import InterCompanyShare
                    from app.models.company import Company
                    
                    # Extract target company (mock logic or simple search)
                    target_company_name = "Settlement Corp" # Mock
                    if "with" in user_input.lower():
                        target_company_name = user_input.lower().split("with")[-1].strip()
                    
                    target_company = db.query(Company).filter(Company.name.ilike(f"%{target_company_name}%")).first()
                    if not target_company:
                         # Fallback to a seeded one if exists
                         target_company = db.query(Company).filter(Company.name != "My Insurance Co").first()

                    if not target_company:
                        response_text = f"Error: Could not find a target company for settlement."
                        event_queue.enqueue_event(new_agent_text_message(response_text))
                        return

                    new_share = InterCompanyShare(
                        from_company_id=uuid.UUID(context.metadata.get("company_id")) if context.metadata.get("company_id") else None,
                        to_company_id=target_company.id,
                        resource_type="claim_settlement",
                        resource_id=uuid.UUID(final_policy_id) if final_policy_id != "UNKNOWN" else None,
                        amount=Decimal("0.0"), # TBD
                        currency="XOF",
                        access_level="full"
                    )
                    db.add(new_share)
                    db.commit()
                    
                    response_text = f"Inter-company settlement initiated with {target_company.name} for policy {final_policy_id}."
                    event_queue.enqueue_event(new_agent_text_message(response_text))
                    return

                req = await self._parse_input(history)
                
                # Override policy_id from context if available
                final_policy_id = policy_id_ctx if policy_id_ctx else req.policy_id
                
                if not final_policy_id or final_policy_id == "UNKNOWN":
                     response_text = "Error: Could not determine Policy ID. Please provide a policy ID for claim processing."
                     event_queue.enqueue_event(new_agent_text_message(response_text))
                     return

                # 3. Process Logic (Fraud Check)
                # We do this BEFORE saving to determine initial status
                # Update request with real policy ID for the check
                req.policy_id = final_policy_id
                
                # Logic from _process_claim (inline or call it)
                # We'll use the existing method but we need to modify it to NOT return a fixed response, 
                # or we just use its logic here.
                # Let's use the method to get the 'status' and 'fraud_score'
                
                mock_resp = self._process_claim(req)
                
                # 4. Persistence
                from app.models.policy import Policy
                from app.models.claim import Claim
                
                # Fetch Policy to get client_id and company_id
                policy = db.query(Policy).filter(Policy.id == uuid.UUID(final_policy_id)).first()
                if not policy:
                    response_text = f"Error: Policy {final_policy_id} not found."
                    event_queue.enqueue_event(new_agent_text_message(response_text))
                    return

                new_claim = Claim(
                    claim_number=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                    policy_id=policy.id,
                    client_id=policy.client_id,
                    company_id=policy.company_id,
                    incident_date=datetime.utcnow().date(), # Default to today if not parsed
                    incident_description=req.description,
                    claim_amount=req.amount,
                    status=mock_resp.status.lower().replace(" ", "_"), # 'Under Review' -> 'under_review'
                    # For now, we accept the DB doesn't have fraud_score column based on previous view_file
                    # We will store it in metadata if possible, or ignore.
                    # Wait, Claim model has no fraud_score column. 
                    # We can append it to description or ignore.
                )
                
                if mock_resp.fraud_score > 0:
                     new_claim.incident_description += f" [Fraud Score: {mock_resp.fraud_score}]"

                db.add(new_claim)
                db.commit()
                db.refresh(new_claim)
                
                # Trigger co-insurance distribution if approved
                if new_claim.status == 'approved':
                    claim_service = ClaimService(db)
                    claim_service._generate_co_insurance_settlements(new_claim)
                
                response_text = f"Claim created successfully! \nClaim ID: {new_claim.claim_number} \nStatus: {mock_resp.status}"
                if mock_resp.message:
                    response_text += f"\nNote: {mock_resp.message}"
                
                event_queue.enqueue_event(new_agent_text_message(response_text))
            
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()

        except Exception as e:
            import traceback
            traceback.print_exc()
            response_text = f"Error processing claim: {str(e)}"
            event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass

