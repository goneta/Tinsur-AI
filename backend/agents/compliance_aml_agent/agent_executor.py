from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
import json

class ComplianceAmlAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="compliance_aml_agent",
            model="gemini-2.0-flash",
            description="Agent for KYC/AML and Sanctions screening",
            instruction="""
            You are a Compliance & AML Specialist. Your role is to screen new user registrations 
            against sanctions lists and assess money laundering risk.
            
            Return a JSON object with the following fields:
            {
                "status": "approved" | "flagged",
                "is_high_risk": boolean,
                "notes": "Reason for the decision",
                "risk_score": 0-100
            }
            """
        )
        
        # Simulated Sanctions List
        self.sanctions_list = [
            "ivan the terrible",
            "notorious biggs", # Simulated name
            "vladimir the impaler",
            "sanctioned_email@example.com"
        ]

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # In this context, user_input is expected to be a JSON string of user details
        try:
            details = json.loads(user_input)
        except:
            details = {"name": user_input}

        full_name = f"{details.get('first_name', '')} {details.get('last_name', '')}".strip().lower()
        email = details.get('email', '').lower()
        
        # 1. Manual Sanctions Check (Simulated)
        flagged = False
        reason = "Manual check passed."
        
        if full_name in self.sanctions_list or email in self.sanctions_list:
            flagged = True
            reason = f"MATCH FOUND ON SANCTIONS LIST: {full_name or email}"

        # 2. LLM Risk Assessment
        google_api_key = context.metadata.get("google_api_key")
        llm_instruction = f"""
        Perform a risk assessment for the following registration:
        Name: {full_name}
        Email: {email}
        Phone: {details.get('phone')}
        Role: {details.get('role')}
        
        Internal Manual Check Status: {'FLAGGED' if flagged else 'CLEAN'}
        Internal Manual Check Reason: {reason}
        
        Evaluate geographical risk (simulated) and role-based risk.
        Return ONLY the JSON object.
        """
        
        llm_response = await self.agent.run(user_input, instruction=llm_instruction, google_api_key=google_api_key)
        
        # If LLM fails or returns non-JSON, fallback to manual check result
        try:
            # Clean LLM response
            cleaned_json = llm_response.replace("```json", "").replace("```", "").strip()
            if "{" in cleaned_json:
                cleaned_json = cleaned_json[cleaned_json.find("{"):cleaned_json.rfind("}")+1]
            response_data = json.loads(cleaned_json)
        except:
            response_data = {
                "status": "flagged" if flagged else "approved",
                "is_high_risk": flagged,
                "notes": f"LLM assessment failed. {reason}",
                "risk_score": 90 if flagged else 10
            }

        # Ensure manual flag overrides LLM if manual check found a match
        if flagged:
            response_data["status"] = "flagged"
            response_data["is_high_risk"] = True
            response_data["notes"] = f"CRITICAL: {reason}. " + response_data.get("notes", "")

        event_queue.enqueue_event(new_agent_text_message(json.dumps(response_data)))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
