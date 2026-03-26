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
            You are a Compliance & AML Specialist. Your role is to screen financial entities 
            (Users, Clients, or Beneficiaries) against sanctions lists and assess money laundering risk.
            
            Contexts:
            - REGISTRATION: Initial platform user signup.
            - ONBOARDING: Manual client record creation.
            - PAYOUT: High-risk screening before releasing claim funds.
            
            Return a JSON object with the following fields:
            {
                "status": "approved" | "flagged",
                "is_high_risk": boolean,
                "notes": "Detailed reason for the decision based on the specific context",
                "risk_score": 0-100,
                "context": "as provided in input"
            }
            """
        )
        
        # Simulated Sanctions List
        self.sanctions_list = [
            "ivan the terrible",
            "notorious biggs",
            "vladimir the impaler",
            "sanctioned_email@example.com",
            "payout_fraudster@danger.com",
            "shadowy corporate entity"
        ]

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        try:
            payload = json.loads(user_input)
        except:
            payload = {"name": user_input, "context": "UNKNOWN"}

        ctx_type = payload.get("context", "REGISTRATION").upper()
        
        # Determine identifiers to check
        identifiers = []
        if payload.get("email"): identifiers.append(payload["email"].lower())
        if payload.get("first_name") and payload.get("last_name"):
            identifiers.append(f"{payload['first_name']} {payload['last_name']}".lower())
        if payload.get("business_name"): identifiers.append(payload["business_name"].lower())
        if payload.get("name"): identifiers.append(payload["name"].lower())

        # 1. Manual Sanctions Check (Simulated)
        flagged = False
        match_found = None
        
        for identifier in identifiers:
            if identifier in self.sanctions_list:
                flagged = True
                match_found = identifier
                break

        # 2. LLM Risk Assessment
        google_api_key = context.metadata.get("google_api_key")
        llm_instruction = f"""
        Perform a {ctx_type} risk assessment:
        Data: {json.dumps(payload, indent=2)}
        
        Internal Manual Check Status: {'FLAGGED' if flagged else 'CLEAN'}
        {'Internal Manual Check Match: ' + match_found if flagged else ''}
        
        Specific Contextual Guidance:
        - If PAYOUT: Be extremely sensitive to mismatching names or high-value amounts.
        - If ONBOARDING: Focus on business legitimacy and geographical risk.
        - If REGISTRATION: Check for spam patterns or burner emails.

        Return ONLY the JSON object.
        """
        
        llm_response = await self.agent.run(user_input, instruction=llm_instruction, google_api_key=google_api_key)
        
        try:
            cleaned_json = llm_response.replace("```json", "").replace("```", "").strip()
            if "{" in cleaned_json:
                cleaned_json = cleaned_json[cleaned_json.find("{"):cleaned_json.rfind("}")+1]
            response_data = json.loads(cleaned_json)
        except:
            response_data = {
                "status": "flagged" if flagged else "approved",
                "is_high_risk": flagged,
                "notes": f"LLM parsing failed. Manual flag: {flagged}",
                "risk_score": 95 if flagged else 15
            }

        # Enforcement
        if flagged:
            response_data["status"] = "flagged"
            response_data["is_high_risk"] = True
            response_data["notes"] = f"MATCH FOUND ON WATCHLIST: {match_found}. " + response_data.get("notes", "")

        response_data["context"] = ctx_type
        event_queue.enqueue_event(new_agent_text_message(json.dumps(response_data)))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
