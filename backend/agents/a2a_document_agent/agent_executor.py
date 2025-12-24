
from a2a.agents.base import BaseAgentExecutor
from a2a.types import AgentTask
from app.core.database import SessionLocal
from app.models.document import Document, DocumentLabel
from app.models.inter_company_share import InterCompanyShare
from app.models.company import Company
from uuid import UUID
import json

class DocumentAgentExecutor(BaseAgentExecutor):
    async def execute(self, task: AgentTask) -> str:
        db = SessionLocal()
        try:
            print(f"[DocumentAgent] Executing: {task.input}")
            # Simplified parsing logic for demo - real agent would use LLM or strict parser
            # In a real setup, we might assume the input is structured JSON if coming from another agent, 
            # or natural language to be processed.
            # Here we implement the core logic functions.
            
            # Logic router (mocking NLP extraction)
            input_text = task.input.lower()
            
            if "share" in input_text:
                return await self.handle_share(db, input_text)
            elif "revoke" in input_text:
                return await self.handle_revoke(db, input_text)
            
            return "Unknown command for Document Agent. I can 'share' or 'revoke' documents."
        except Exception as e:
            return f"Error executing document task: {str(e)}"
        finally:
            db.close()

    async def handle_share(self, db, text):
        # Expected format (implied): "Share [Doc Name] with [Company Name] scope [B2B/B2C] option [1/2] rule [A/B/C]"
        # This is complex to parse via string matching.
        # Ideally, we accept JSON payload for precise control.
        # Fallback to a placeholder response for the agent structure verification.
        return "Sharing logic initialized. (To be connected to structured inputs)"
        
    async def handle_revoke(self, db, text):
        return "Revocation logic initialized."

    # Core logic functions to be used by tool calls or structured inputs
    def share_document_logic(self, db, doc_id, target_company_id, scope, option_shareable, rule_reshare):
        """
        Implements the strict logic:
        Option 1: Not Shareable
        Option 2: Shareable (with sub-rules A, B, C)
        """
        # Validate logic
        if not option_shareable and rule_reshare:
            # If not shareable, rule is irrelevant (effectively C)
            rule_reshare = None
            
        share = InterCompanyShare(
            resource_type='document',
            resource_id=doc_id, # Linking logic
            document_id=doc_id,
            to_company_id=target_company_id,
            # We need from_company_id - context usually provides this. 
            # For now mocking or requiring explicit arg.
             from_company_id=UUID("00000000-0000-0000-0000-000000000000"), # Placeholder
            scope=scope,
            is_reshareable=option_shareable,
            reshare_rule=rule_reshare
        )
        db.add(share)
        db.commit()
        return share
