from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from models import QuoteRequest, QuoteResponse
from app.core.database import SessionLocal
from app.models.client import Client
from app.models.client_details import ClientAutomobile, ClientHousing, ClientHealth, ClientLife
from app.models.quote import Quote
from app.models.policy_type import PolicyType
import json
import uuid
import re
import asyncio

class QuoteAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="quote_agent",
            model="gemini-3-flash-preview",
            description="Agent that calculates quotes",
            instruction="""
            You are a Quote Agent.
            Collect all necessary information from the user:
            - Client Name
            - Policy Type
            - Coverage Amount
            - Duration (months)
            - Payment Frequency
            - Vehicle Value
            - Vehicle Age (year)
            - Vehicle Mileage
            - Vehicle Registration Number
            - Driver Date of Birth
            - Driver Licence Number
            - Manual Discount
            Ask for them one by one if missing.
            """,
        )

    async def _extract_fields(self, history: list) -> QuoteRequest:
        """Uses Gemini to extract field values from chat history (Structured Output)."""
        if not history:
            return QuoteRequest(manual_discount=0.0)

        history_text = ""
        for h in history:
            role = "User" if h["role"] == "user" else "Assistant"
            text = h["text"]
            history_text += f"{role}: {text}\n"

        extraction_instruction = """
        Analyze the conversation history and extract insurance quote details.
        - Map types like 'auto', 'car' to 'Automobile'.
        - Map 'home', 'house' to 'Housing'.
        - Extract numeric values for amounts, coverage, value, mileage, and year.
        - If a field is not mentioned, keep it as null.
        - Manual discount defaults to 0.0 unless specified.
        """

        try:
            # Using Gemini-2.0-flash for high performance extraction with structured output
            extractor = Agent(
                name="quote_extractor",
                model="gemini-3-flash-preview",
                instruction=extraction_instruction,
                output_type=QuoteRequest
            )
            
            # Use run but handle potential serializability/execution context issues if any
            extracted = await extractor.run(f"Extract from this history:\n\n{history_text}")
            
            # Ensure it's a QuoteRequest object
            if isinstance(extracted, QuoteRequest):
                return extracted
            elif isinstance(extracted, dict):
                return QuoteRequest(**extracted)
            return QuoteRequest(manual_discount=0.0)
            
        except Exception as e:
            print(f"Structured Extraction Error: {e}. Falling back to empty request.")
            return QuoteRequest(manual_discount=0.0)

    def _load_from_db(self, req: QuoteRequest, context_metadata: dict):
        """Tries to fill missing fields from the database if user/client is known."""
        # SECURITY: Enforce company_id isolation
        company_id = context_metadata.get("company_id")
        user_id = context_metadata.get("user_id")
        if not company_id or not user_id:
            return

        db = SessionLocal()
        try:
            # Find client by user_id AND company_id
            client = db.query(Client).filter(
                Client.user_id == uuid.UUID(str(user_id)),
                Client.company_id == uuid.UUID(str(company_id))
            ).first()
            if not client:
                return
            
            # Fill basic fields if missing
            if not req.client_name:
                req.client_name = f"{client.first_name} {client.last_name}"
            
            # Fill policy-specific fields
            policy_type = (req.policy_type or "").lower()
            if "auto" in policy_type:
                detail = db.query(ClientAutomobile).filter(ClientAutomobile.client_id == client.id).first()
                if detail:
                    if not req.vehicle_value: req.vehicle_value = float(detail.vehicle_value) if detail.vehicle_value else None
                    if not req.vehicle_age: req.vehicle_age = detail.vehicle_age
                    if not req.vehicle_mileage: req.vehicle_mileage = detail.vehicle_mileage
                    if not req.vehicle_registration: req.vehicle_registration = detail.vehicle_registration
                    if not req.license_number: req.license_number = detail.license_number
                    if not req.driver_dob and detail.driver_dob: req.driver_dob = detail.driver_dob.strftime("%Y-%m-%d")

        except Exception as e:
            print(f"DB Lookup Error: {e}")
        finally:
            db.close()

    def _calculate_quote(self, request: QuoteRequest) -> QuoteResponse:
        """Business Logic for Pricing."""
        # Simple math for demo
        val = request.vehicle_value or request.coverage_amount or 10000.0
        base_premium = val * 0.05
        
        # Adjust for duration
        duration_factor = (request.duration_months or 12) / 12
        final_premium = base_premium * duration_factor
        
        # Apply discount
        discount_amount = final_premium * ((request.manual_discount or 0) / 100)
        final_premium -= discount_amount
        
        details = f"Calculated based on {request.policy_type}. Base Premium: ${base_premium}. Discount: ${discount_amount}."
        
        return QuoteResponse(
            quote_id=f"Q-{uuid.uuid4().hex[:8].upper()}",
            premium_yearly=round(final_premium, 2),
            premium_monthly=round(final_premium / 12, 2),
            details=details
        )

    def _persist_quote(self, req: QuoteRequest, resp: QuoteResponse, context_metadata: dict):
        """Saves final quote to DB."""
        db = SessionLocal()
        try:
            user_id = context_metadata.get("user_id")
            company_id = context_metadata.get("company_id")
            
            client_id = None
            if user_id and company_id:
                client = db.query(Client).filter(
                    Client.user_id == uuid.UUID(str(user_id)),
                    Client.company_id == uuid.UUID(str(company_id))
                ).first()
                if client:
                    client_id = client.id

            if not company_id:
                print("Cannot persist quote: company_id missing")
                return

            # Match policy type
            pt_code = (req.policy_type or "").lower()
            if "auto" in pt_code: pt_code = "automobile"
            elif "home" in pt_code or "house" in pt_code: pt_code = "housing"
            
            policy_type = db.query(PolicyType).filter(
                PolicyType.company_id == uuid.UUID(str(company_id)),
                PolicyType.code.ilike(pt_code)
            ).first()

            new_quote = Quote(
                id=uuid.uuid4(),
                company_id=uuid.UUID(str(company_id)),
                client_id=client_id,
                policy_type_id=policy_type.id if policy_type else None,
                quote_number=resp.quote_id,
                coverage_amount=req.coverage_amount,
                premium_amount=resp.premium_yearly,
                final_premium=resp.premium_yearly,
                premium_frequency=req.payment_frequency or 'annual',
                duration_months=req.duration_months or 12,
                status='draft',
                details={
                    "vehicle_value": req.vehicle_value,
                    "vehicle_age": req.vehicle_age,
                    "vehicle_mileage": req.vehicle_mileage,
                    "vehicle_registration": req.vehicle_registration,
                }
            )
            
            if user_id:
                new_quote.created_by = uuid.UUID(str(user_id))

            db.add(new_quote)
            db.commit()
            print(f"Quote {resp.quote_id} persisted successfully.")
        except Exception as e:
            print(f"Persistence error: {e}")
            db.rollback()
        finally:
            db.close()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Build history from context events OR metadata
        history = context.metadata.get("history", [])
        if not history and context.events:
            for event in context.events:
                history.append({
                    "role": "user" if event.type == "user_text_message" else "assistant",
                    "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                    "type": event.type
                })

        req = await self._extract_fields(history)
        
        # Try to enrich from database
        self._load_from_db(req, context.metadata)
        
        # Check for missing fields
        missing_fields = []
        if not req.client_name: missing_fields.append(("Client Name", "client_name", "What is the client's full name?"))
        if not req.policy_type: missing_fields.append(("Policy Type", "policy_type", "What type of policy is this? (e.g. Automobile, Housing)"))
        if not req.coverage_amount: missing_fields.append(("Coverage Amount", "coverage_amount", "What is the requested coverage amount?"))
        if not req.duration_months: missing_fields.append(("Duration", "duration_months", "How many months should the policy last?"))
        if not req.payment_frequency: missing_fields.append(("Payment Frequency", "payment_frequency", "What is the payment frequency? (e.g. Monthly, Annual)"))
        
        is_auto = req.policy_type and "auto" in req.policy_type.lower()
        if is_auto:
            if not req.vehicle_value: missing_fields.append(("Vehicle Value", "vehicle_value", "What is the estimated value of the vehicle?"))
            if not req.vehicle_age: missing_fields.append(("Vehicle Year", "vehicle_age", "What is the registration year of the vehicle?"))
            if not req.vehicle_mileage: missing_fields.append(("Vehicle Mileage", "vehicle_mileage", "What is the current mileage of the vehicle?"))
            if not req.vehicle_registration: missing_fields.append(("Registration #", "vehicle_registration", "What is the vehicle registration number?"))
            if not req.license_number: missing_fields.append(("License #", "license_number", "What is the driver's license number?"))
            if not req.driver_dob: missing_fields.append(("Driver DOB", "driver_dob", "What is the driver's date of birth? (YYYY-MM-DD)"))

        # If missing anything, ask for the first one and provide current progress
        if missing_fields:
            label, key, question = missing_fields[0]
            
            # Prepare a progress state for the UI
            progress_data = {
                "type": "quote_progress",
                "current_step": label,
                "missing_count": len(missing_fields),
                "total_fields": 5 + (6 if is_auto else 0),
                "extracted_data": req.model_dump(),
                "next_question": question
            }
            
            response_text = f"{question}\n\n```json\n{json.dumps({'interaction': {'type': 'progress', 'data': progress_data}}, indent=2)}\n```"
            event_queue.enqueue_event(new_agent_text_message(response_text))
            return

        # If everything is there, calculate, persist, and show preview
        resp = self._calculate_quote(req)
        
        # Persist to DB
        self._persist_quote(req, resp, context.metadata)
        
        response_data = {
            "type": "quote",
            "client_name": req.client_name,
            "quote_number": resp.quote_id,
            "premium_amount": resp.premium_yearly,
            "base_premium": resp.premium_yearly + (resp.premium_yearly * 0.1), # Mocked markup
            "risk_adjustment": "Included",
            "discount_percent": req.manual_discount or 0.0,
            "discount_amount": (resp.premium_yearly * (req.manual_discount or 0) / 100),
            "policy_type": req.policy_type,
            "coverage_amount": req.coverage_amount,
            "status": "DRAFT",
            "valid_until": "January 12, 2026",
            "payment_frequency": req.payment_frequency or "monthly payment",
            "coverage_details": resp.details,
            "duration_months": req.duration_months,
            "vehicle_value": req.vehicle_value,
            "vehicle_age": req.vehicle_age,
            "vehicle_mileage": req.vehicle_mileage,
            "vehicle_registration": req.vehicle_registration,
            "license_number": req.license_number,
            "driver_dob": req.driver_dob
        }
        
        # Interaction list for "Modify"
        interaction_data = {
            "interaction": {
                "type": "modify",
                "entity": "quote",
                "data": response_data,
                "fields": [
                    {"label": "Client Name", "key": "client_name", "value": req.client_name},
                    {"label": "Policy Type", "key": "policy_type", "value": req.policy_type},
                    {"label": "Coverage Amount", "key": "coverage_amount", "value": req.coverage_amount},
                    {"label": "Duration (Months)", "key": "duration_months", "value": req.duration_months},
                    {"label": "Payment Frequency", "key": "payment_frequency", "value": req.payment_frequency}
                ]
            }
        }
        
        if is_auto:
            interaction_data["interaction"]["fields"].extend([
                {"label": "Vehicle Value", "key": "vehicle_value", "value": req.vehicle_value},
                {"label": "Vehicle Year", "key": "vehicle_age", "value": req.vehicle_age},
                {"label": "Vehicle Mileage", "key": "vehicle_mileage", "value": req.vehicle_mileage},
                {"label": "Registration #", "key": "vehicle_registration", "value": req.vehicle_registration},
                {"label": "License #", "key": "license_number", "value": req.license_number},
                {"label": "Driver DOB", "key": "driver_dob", "value": req.driver_dob}
            ])
        
        interaction_data["interaction"]["fields"].append({"label": "Manual Discount", "key": "manual_discount", "value": req.manual_discount})

        response_text = f"I have calculated the quote for you. It has been saved as a **DRAFT** in your account.\n\n```json\n{json.dumps(response_data, indent=2)}\n```\n\nYou can also modify any detail using the list below or approve it to proceed.\n\n```json\n{json.dumps(interaction_data, indent=2)}\n```"
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
