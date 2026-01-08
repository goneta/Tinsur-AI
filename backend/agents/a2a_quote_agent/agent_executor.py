from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .models import QuoteRequest, QuoteResponse
from app.core.database import SessionLocal
from app.models.client import Client
from app.services.premium_policy_service import PremiumPolicyService
from app.services.quote_service import QuoteService
from app.repositories.quote_repository import QuoteRepository
import json
import uuid
import re
import asyncio

class QuoteAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="quote_agent",
            model="gemini-3-flash-preview",
            description="Agent that calculates quotes based on eligible premium policies.",
            instruction="""
            You are a Quote Agent.
            Your goal is to help the client get an insurance quote.
            1. Identify the client (from logged in context).
            2. Check eligibility for Premium Policies.
            3. If information is missing (accidents, license years, etc), ASK the user for it specifically.
            4. If multiple policies are available, ask the user to choose one.
            5. Once a policy is selected, ask for Coverage Amount and Duration if not provided.
            6. Generate the quote using the backend system.
            """,
        )

    async def _extract_fields(self, history: list) -> QuoteRequest:
        """Uses Gemini to extract field values from chat history."""
        if not history:
            return QuoteRequest()

        history_text = ""
        for h in history:
            role = "User" if h["role"] == "user" else "Assistant"
            text = h["text"]
            history_text += f"{role}: {text}\n"

        # Expanded extraction instruction to capture policy choice and eligibility fields
        extraction_instruction = """
        Analyze the conversation history. Extract insurance quote details and client eligibility updates.
        
        Fields to extract:
        - policy_choice: (string) The name or code of the policy the user selected (e.g. "Gold", "Silver", "Automobile").
        - coverage_amount: (number)
        - duration_months: (number)
        
        Eligibility Updates (if mentioned):
        - accident_count: (int)
        - no_claims_years: (int)
        - driving_license_years: (int)
        - employment_status: (string)
        
        If a field is not mentioned, keep it as null.
        """

        try:
            # We reuse QuoteRequest model but it might need dynamic fields for eligibility updates.
            # For strict typing, we relying on the model to have these or use a dict.
            # QuoteRequest in models.py likely needs updates or we returned a dict.
            # Let's return a dict here to be flexible, then map to object.
            
            extractor = Agent(
                name="quote_extractor",
                model="gemini-3-flash-preview",
                instruction=extraction_instruction,
                output_type=dict 
            )
            
            extracted = await extractor.run(f"Extract from this history:\n\n{history_text}")
            
            # Map valid keys to QuoteRequest, put others in 'risk_factors' or distinct dict
            # Actually, let's just return the dict for internal use in execute
            return extracted
            
        except Exception as e:
            print(f"Extraction Error: {e}")
            return {}

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # 1. Build History
        history = context.metadata.get("history", [])
        if not history and context.events:
            for event in context.events:
                history.append({
                    "role": "user" if event.type == "user_text_message" else "assistant",
                    "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                })

        # 2. Context & Auth
        company_id = context.metadata.get("company_id")
        user_id = context.metadata.get("user_id")
        
        if not company_id or not user_id:
             event_queue.enqueue_event(new_agent_text_message("I cannot process your request without organization context."))
             return

        db = SessionLocal()
        try:
            # 3. Identify Client
            client = db.query(Client).filter(
                Client.user_id == uuid.UUID(str(user_id)),
                Client.company_id == uuid.UUID(str(company_id))
            ).first()
            
            if not client:
                 event_queue.enqueue_event(new_agent_text_message("I could not find your client profile. Please contact support."))
                 return

            # 4. Extract User Input (Policy Choice, Eligibility Updates)
            extracted = await self._extract_fields(history)
            
            # 4b. Update Client with extracted eligibility info if provided
            # (In a real flow, we might want to confirm before saving, but for agent speed we save)
            param_updates = []
            if extracted.get("accident_count") is not None:
                client.accident_count = int(extracted["accident_count"])
                param_updates.append("accident count")
            if extracted.get("no_claims_years") is not None:
                 client.no_claims_years = int(extracted["no_claims_years"])
                 param_updates.append("no claims years")
            if extracted.get("driving_license_years") is not None:
                 client.driving_license_years = int(extracted["driving_license_years"])
                 param_updates.append("driving license years")
            if extracted.get("employment_status") is not None:
                 client.employment_status = str(extracted["employment_status"])
                 param_updates.append("employment status")
            
            if param_updates:
                db.commit()
                # event_queue.enqueue_event(new_agent_text_message(f"Updated your profile: {', '.join(param_updates)}."))

            # 5. Run Matching Logic
            policy_service = PremiumPolicyService(db)
            match_result = policy_service.match_eligible_policies(uuid.UUID(str(company_id)), client.id)
            
            # --- BLOCKING FLOW: Missing Info ---
            if match_result["status"] == "missing_info":
                missing = match_result["missing_fields"]
                # Ask for the first missing field
                field = missing[0]
                # improved phrasing map
                questions = {
                    "Accident Count": "How many accidents have you had in the last 3 years?",
                    "No Claims Years": "How many years of No Claims Bonus do you have?",
                    "Driving License Years": "How many years have you held your driving license?",
                    "Employment Status": "What is your current employment status? (Employed, Self-Employed, etc)",
                }
                question = questions.get(field, f"Please provide your {field}.")
                
                event_queue.enqueue_event(new_agent_text_message(
                    f"To check your eligibility, I need a bit more info. {question}"
                ))
                return

            # --- BLOCKING FLOW: No Policies ---
            if match_result["status"] == "no_policies":
                 event_queue.enqueue_event(new_agent_text_message(
                    f"I'm sorry, but based on your profile, we currently have no eligible premium policies available for you."
                ))
                 return

            # --- SELECTION FLOW: Multiple Policies ---
            eligible_policies = match_result["data"]
            recommended_id = match_result.get("recommended_id")
            
            # Check if user has already selected a policy from the list
            selected_policy = None
            user_choice = extracted.get("policy_choice")
            
            if user_choice:
                # Fuzzy match user choice against eligible policies
                for p in eligible_policies:
                    if user_choice.lower() in p.name.lower() or p.name.lower() in user_choice.lower():
                        selected_policy = p
                        break
            
            # If no selection or invalid selection, present options
            if not selected_policy:
                options_text = "I found the following policies for you:\n"
                for p in eligible_policies:
                    rec = " (Recommended)" if p.id == recommended_id else ""
                    options_text += f"- **{p.name}**: {p.price} / month{rec}\n"
                
                options_text += "\nWhich one would you like to choose?"
                event_queue.enqueue_event(new_agent_text_message(options_text))
                return

            # --- CALCULATION FLOW ---
            # We have a selected policy. Now check calculation params.
            coverage = extracted.get("coverage_amount")
            if not coverage:
                 event_queue.enqueue_event(new_agent_text_message(
                    f"You selected {selected_policy.name}. What coverage amount (XOF) are you looking for?"
                ))
                 return
                 
            # Proceed to Calculate
            quote_service = QuoteService(QuoteRepository(db))
            
            # Risk factors can include client details + vehicle details mock
            risk_factors = {
                "age": 30, # default or calc from dob
                "vehicle_value": coverage, # simplistic assumption for generic quote
                **extracted
            }
            
            calculation = quote_service.calculate_premium(
                risk_factors=risk_factors,
                duration_months=str(extracted.get("duration_months") or 12),
                policy_id=selected_policy.id,
                company_id=uuid.UUID(str(company_id))
            )
            
            # Persist Quote
            # Note: create_quote requires many args, simplifying for agent demo
            quote = quote_service.create_quote(
                company_id=uuid.UUID(str(company_id)),
                client_id=client.id,
                policy_type_id=selected_policy.id,
                coverage_amount=float(coverage),
                risk_factors=risk_factors,
                premium_frequency="annual",
                duration_months=int(extracted.get("duration_months") or 12),
                discount_percent=0,
                created_by=client.user_id # Self-service
            )
            
            response_text = f"""
I have generated a quote for you based on the **{selected_policy.name}** policy.

**Quote Reference:** {quote.quote_number}
**Premium:** {calculation['final_premium']} XOF / year
**Monthly:** {calculation['monthly_installment']} XOF / month

This quote has been saved to your account.
"""
            event_queue.enqueue_event(new_agent_text_message(response_text))

        except Exception as e:
            print(f"Agent Execution Error: {e}")
            event_queue.enqueue_event(new_agent_text_message("I encountered an error while processing your request. Please try again later."))
        finally:
            db.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
