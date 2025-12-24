from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from models import PolicyCreationRequest, PolicyResponse
from app.core.database import SessionLocal
from app.models.quote import Quote
from app.models.policy_type import PolicyType
from app.models.policy import Policy
from sqlalchemy.orm import joinedload
import json
import uuid
from datetime import datetime, timedelta

class PolicyAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="policy_agent",
            model="gemini-3-flash-preview",
            description="Agent that manages policies and risk",
            instruction="""
            You are a Policy Agent.
            Manage policies and score risk.
            If the user wants to 'create a policy', fetch draft quotes first.
            """,
        )

    def _get_draft_quotes(self, db_session, company_id: str = None):
        """Fetch quotes with status 'draft' or 'accepted' or 'sent' for a specific company."""
        query = db_session.query(Quote).options(joinedload(Quote.policy_type))
        
        if company_id:
            query = query.filter(Quote.company_id == uuid.UUID(str(company_id)))
            
        quotes = query.filter(
            Quote.status.in_(['draft', 'accepted', 'sent'])
        ).order_by(Quote.created_at.desc()).all()
        
        return [
            {
                "id": str(q.id),
                "quote_number": q.quote_number,
                "client_name": q.client_name,
                "policy_type": q.policy_type.name if q.policy_type else "General",
                "created_at": q.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for q in quotes
        ]

    async def _parse_input(self, history: list) -> PolicyCreationRequest:
        """Uses Gemini to extract policy details from chat history (Structured Output)."""
        if not history:
            return PolicyCreationRequest()

        history_text = ""
        for h in history:
            role = "User" if h["role"] == "user" else "Assistant"
            text = h["text"]
            history_text += f"{role}: {text}\n"

        extraction_instruction = """
        Analyze the conversation history and extract policy creation details.
        - Extract the quote_id if mentioned (format like Q-XXXXX).
        - Extract the start_date if mentioned (as YYYY-MM-DD).
        - If a field is not mentioned, keep it as null.
        """

        try:
            extractor = Agent(
                name="policy_extractor",
                model="gemini-3-flash-preview",
                instruction=extraction_instruction,
                output_type=PolicyCreationRequest
            )
            
            extracted = await extractor.run(f"Extract from this history:\n\n{history_text}")
            
            if isinstance(extracted, PolicyCreationRequest):
                return extracted
            elif isinstance(extracted, dict):
                return PolicyCreationRequest(**extracted)
            return PolicyCreationRequest()
        except Exception as e:
            print(f"Policy Extraction Error: {e}. Falling back to empty request.")
            return PolicyCreationRequest()

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
            # Security & DB setup
            user_id = context.metadata.get("user_id")
            if not user_id:
                event_queue.enqueue_event(new_agent_text_message("User ID not found in context."))
                return

            db = SessionLocal()
            try:
                # Check for "create a policy" or keywords
                if "create" in user_input.lower() and "policy" in user_input.lower():
                    quotes = self._get_draft_quotes(db, context.metadata.get("company_id"))
                    
                    response_data = {
                        "type": "quote_selection",
                        "data": {
                            "quotes": quotes
                        }
                    }
                    
                    response_text = f"I found {len(quotes)} draft quotes. Which one would you like to convert into a policy?\n\n```json\n{json.dumps(response_data, indent=2)}\n```"
                    event_queue.enqueue_event(new_agent_text_message(response_text))
                    return

                # Normal Policy Creation Flow (if Quote ID provided)
                req = await self._parse_input(history)
                if not req.quote_id or "UNKNOWN" in req.quote_id:
                     response_text = "Please select a quote from the list or provide a quote number to create a policy."
                else:
                     # Look up quote with company isolation
                     company_id = context.metadata.get("company_id")
                     query = db.query(Quote)
                     if company_id:
                         query = query.filter(Quote.company_id == uuid.UUID(str(company_id)))
                     
                     quote = query.filter(Quote.quote_number == req.quote_id).first()
                     if not quote:
                         try:
                             quote = query.filter(Quote.id == uuid.UUID(req.quote_id)).first()
                         except:
                             pass
                     
                     if quote:
                         policy_id = f"POL-{uuid.uuid4().hex[:8].upper()}"
                         new_policy = Policy(
                             id=uuid.uuid4(),
                             company_id=quote.company_id,
                             client_id=quote.client_id,
                             policy_type_id=quote.policy_type_id,
                             quote_id=quote.id,
                             policy_number=policy_id,
                             coverage_amount=quote.coverage_amount,
                             premium_amount=quote.final_premium,
                             start_date=datetime.now().date(),
                             end_date=(datetime.now() + timedelta(days=365)).date(),
                             status='active',
                             created_by=uuid.UUID(str(user_id))
                         )
                         db.add(new_policy)
                         
                         # Update quote status
                         quote.status = 'accepted'
                         
                         db.commit()
                         
                         response_data = {
                             "type": "policy",
                             "policy_number": policy_id,
                             "quote_number": quote.quote_number,
                             "status": "ACTIVE",
                             "effective_date": new_policy.start_date.isoformat(),
                             "expiry_date": new_policy.end_date.isoformat()
                         }
                         response_text = f"Policy {policy_id} has been created successfully based on Quote {quote.quote_number}. It is now active!\n\n```json\n{json.dumps(response_data, indent=2)}\n```"
                     else:
                         response_text = f"Could not find quote '{req.quote_id}'. Please make sure you provide a valid quote number."
                
                event_queue.enqueue_event(new_agent_text_message(response_text))

            finally:
                db.close()

        except Exception as e:
            import traceback
            error_msg = f"Error in Policy Agent: {str(e)}\n{traceback.format_exc()}"
            event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
