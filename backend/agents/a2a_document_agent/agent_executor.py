from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from app.core.database import SessionLocal
from app.models.document import Document, DocumentLabel
from app.models.inter_company_share import InterCompanyShare
from app.models.company import Company
from uuid import UUID
import json

class DocumentAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="document_agent",
            model="gemini-2.5-flash",
            description="Agent that manages insurance documents and sharing",
            instruction="""
            You are a Document Management Specialist for InsurSaaS.
            You can help with document sharing, revocation, and metadata management.
            ALWAYS verify the company_id in the context before performing actions.
            """,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        company_id = context.metadata.get("company_id")
        if not company_id:
            event_queue.enqueue_event(new_agent_text_message("Error: Missing company_id in context. I cannot access document records."))
            return

        db = SessionLocal()
        try:
            input_text = user_input.lower()
            
            if "share" in input_text:
                result = "Sharing logic initialized for company " + str(company_id)
            elif "revoke" in input_text:
                result = "Revocation logic initialized for company " + str(company_id)
            else:
                result = "I am ready to help with documents. I can 'share' or 'revoke' access."
            
            event_queue.enqueue_event(new_agent_text_message(result))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Document Agent Error: {str(e)}"))
        finally:
            db.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass

    # Core logic functions for internal use or future tool expansion
    def share_document_logic(self, db, company_id, doc_id, target_company_id, scope, option_shareable, rule_reshare):
        if not option_shareable and rule_reshare:
            rule_reshare = None
            
        share = InterCompanyShare(
            resource_type='document',
            resource_id=doc_id,
            document_id=doc_id,
            to_company_id=target_company_id,
            from_company_id=UUID(company_id),
            scope=scope,
            is_reshareable=option_shareable,
            reshare_rule=rule_reshare
        )
        db.add(share)
        db.commit()
        return share
