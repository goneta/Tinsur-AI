from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import get_eligible_policies, update_client_profile, generate_insurance_quote
from app.core.database import SessionLocal
from app.models.client import Client
import uuid

class QuoteAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="quote_agent",
            model="gemini-2.0-flash-exp", # Using latest experimental model
            description="Agent that calculates quotes based on eligible premium policies.",
            instruction="""
            You are the Tinsur.AI Quote Agent.
            Your goal is to help the client get an insurance quote.
            
            OPERATIONAL CONTEXT:
            - You have access to the user's Client ID and Company ID. You MUST use these in tool calls.
            - Follow the steps below strictly.
            
            CRITICAL INSTRUCTION:
            - **DO NOT** output the function call as text (e.g., do not write "get_eligible_policies(...)").
            - **USE THE TOOL DIRECTLY**. The system will execute it for you.
            - If you need to check eligibility, generate the Tool Call, do not describe it.

            WORKFLOW:
            1. **CHECK ELIGIBILITY**: Use the `get_eligible_policies` tool with `client_id` and `company_id`.
            2. **ANALYZE RESULT**:
               - If it returns "status": "missing_info", ASK the user for the missing fields (e.g. "accident_count").
               - If status is "success", it will list eligible policies.
            3. **UPDATE PROFILE** (If user provides missing info):
               - If user answers with info (e.g. "I have 0 accidents"), call `update_client_profile`.
               - THEN call `get_eligible_policies` again to refresh.
            4. **SELECT POLICY**:
               - Present the eligible policies (Name, Price).
               - Ask user to choose one.
            5. **FINALIZE & QUOTE**:
               - Once policy is chosen and "coverage_amount" is known (ask if not), call `generate_insurance_quote`.
               - Display the quote results nicely.
               
            Refusal:
            - If user asks about claims, support tickets, or irrelevant topics, politely respond that you can only help with quotes and refer them to the main menu (or Manager).
            """,
            tools=[get_eligible_policies, update_client_profile, generate_insurance_quote]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # 1. Build History
        history = context.metadata.get("history", [])
        if not history and context.events:
             for event in context.events:
                  history.append({
                       "role": "user" if event.type == "user_text_message" else "assistant",
                       "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                  })
        
        # 2. Extract User Input from latest event if not in history
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                  if event.type == "user_text_message":
                      user_input = event.text
                      break
        
        if not user_input:
            return

        # 3. Resolve Context IDs
        company_id = context.metadata.get("company_id")
        user_id = context.metadata.get("user_id")
        
        if not company_id or not user_id:
             event_queue.enqueue_event(new_agent_text_message("I cannot process your request without organization context."))
             return

        db = SessionLocal()
        try:
            client = db.query(Client).filter(
                Client.user_id == uuid.UUID(str(user_id)),
                Client.company_id == uuid.UUID(str(company_id))
            ).first()
            
            if not client:
                 event_queue.enqueue_event(new_agent_text_message("I could not find your client profile. Please contact support."))
                 return
            
            # 4. Construct Prompt with Context
            # We append the context variables so the LLM knows what to pass to tools
            context_prompt = f"""
            
            [SYSTEM CONTEXT VARIABLES]
            Client_ID: {client.id}
            Company_ID: {company_id}
            User_ID: {user_id}
            
            [CONVERSATION HISTORY]
            """
            for h in history:
                role = "User" if h["role"] == "user" else "Assistant"
                text = h["text"] if "text" in h else h["content"]
                context_prompt += f"{role}: {text}\n"
            
            context_prompt += f"\nUser: {user_input}"
            
            # 5. Run Agent
            response_text = await self.agent.run(context_prompt, google_api_key=context.metadata.get("google_api_key"))
            
            # --- MANUAL TOOL EXECUTION FALLBACK ---
            # If the model output raw code instead of executing the tool, we intercept it here.
            import re
            import json
            
            # Check for get_eligible_policies
            if "get_eligible_policies" in response_text and "(" in response_text:
                print("DEBUG: Intercepting raw tool call for get_eligible_policies")
                # Simple extraction of UUIDs
                ids = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', response_text)
                if len(ids) >= 2:
                    c_id, co_id = ids[0], ids[1] # Warning: Order matters. Usually client_id, company_id.
                    # Verify order based on prompt text if possible, but assuming standard prompt flow:
                    # The user prompt has Client_ID first usually.
                    # Actually, let's use the IDs from the CONTEXT variables (lines 96-97) to be safe,
                    # because we know what they should be!
                    
                    # Execute tool with Verified IDs
                    tool_result_json = get_eligible_policies(str(client.id), str(company_id))
                    
                    try:
                        result_data = json.loads(tool_result_json)
                        if result_data.get("status") == "success":
                            policies = result_data.get("eligible_policies", [])
                            policy_list = "\n".join([f"- **{p['name']}**: {p['description']} (Premium: {p['estimated_premium']})" for p in policies])
                            response_text = f"I've found the following eligible policies for you:\n\n{policy_list}\n\nWhich one would you like to proceed with?"
                        elif result_data.get("status") == "missing_info":
                            missing = ", ".join(result_data.get("missing_fields", []))
                            response_text = f"To provide accurate policies, I need a bit more information. Could you please provide your: {missing}?"
                        else:
                            response_text = f"I checked your eligibility, but unfortunately: {result_data.get('message', 'No policies found.')}"
                    except:
                        response_text = f"System: Tool execution failed. Raw result: {tool_result_json}"

            event_queue.enqueue_event(new_agent_text_message(response_text))
            
        except Exception as e:
            print(f"Quote Agent Error: {e}")
            event_queue.enqueue_event(new_agent_text_message(f"I encountered a system error: {str(e)}"))
        finally:
            db.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
