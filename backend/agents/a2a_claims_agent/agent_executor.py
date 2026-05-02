from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .models import ClaimRequest, ClaimResponse
import json
from app.core.database import SessionLocal
from app.core.security_context import SecurityService
from app.services.ai_action_control_service import (
    AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS,
    AiActionControlService,
    RestrictedInsuranceOperation,
)

class ClaimsAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="claims_agent",
            model="gemini-2.0-flash",
            description="Agent that processes claims and detects fraud",
            instruction=f"""
            You are a Claims Agent.
            Analyze incidents for claim triage, fraud indicators, explanatory guidance, and draft intake notes.

            {AI_CONSEQUENTIAL_ACTION_INSTRUCTIONS}
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
                model="gemini-2.0-flash",
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
        
        amount = float(request.amount or 0)
        description = request.description or ""

        # Rule 1: High Amount
        if amount > 5000:
            fraud_score += 30
            
        # Rule 2: Suspicious Keywords
        suspicious_words = ["stolen", "lost", "cash", "unknown"]
        if any(w in description.lower() for w in suspicious_words):
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

                # 2. Parse Input and enforce AI action controls before any legal/financial record mutation.
                req = await self._parse_input(history)
                final_policy_id = policy_id_ctx if policy_id_ctx else req.policy_id
                control = AiActionControlService()

                if "share" in user_input.lower() or "settle" in user_input.lower():
                    payload = control.restricted_response(
                        RestrictedInsuranceOperation.SETTLE_CLAIM,
                        requested_by="claims_agent.execute",
                        record_reference=final_policy_id,
                        next_step="Prepare settlement context and send it to deterministic inter-company settlement services for authorization."
                    )
                    payload["settlement_triage_draft"] = {
                        "policy_id": final_policy_id,
                        "user_request": user_input,
                        "recommended_next_step": "Validate coverage, counterparty, amount, and authorization outside the AI layer before creating settlement records."
                    }
                    event_queue.enqueue_event(new_agent_text_message(json.dumps(payload, sort_keys=True)))
                    return

                mock_resp = self._process_claim(req)
                payload = control.restricted_response(
                    RestrictedInsuranceOperation.CREATE_CLAIM_RECORD,
                    requested_by="claims_agent.execute",
                    record_reference=final_policy_id,
                    next_step="Submit this triage draft to deterministic claims intake for validation, authorization, and auditable record creation."
                )
                payload["claim_triage_draft"] = {
                    "policy_id": final_policy_id,
                    "incident_description": req.description,
                    "estimated_amount": req.amount,
                    "incident_date": req.incident_date,
                    "triage_status": mock_resp.status,
                    "fraud_score": mock_resp.fraud_score,
                    "triage_message": mock_resp.message,
                }
                event_queue.enqueue_event(new_agent_text_message(json.dumps(payload, sort_keys=True)))
                return

            
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

