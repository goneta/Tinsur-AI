from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import get_eligible_policies, update_client_profile, generate_insurance_quote, search_clients, list_recent_clients
from app.core.database import SessionLocal
from app.models.client import Client, client_company
from app.services.ai_context_service import build_tenant_context_summary
import uuid
import json
import re

class QuoteAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="quote_agent",
            model="gemini-2.0-flash", # Using latest experimental model
            description="Agent that calculates quotes based on eligible premium policies.",
            instruction="""
            You are the Tinsur.AI Quote Agent.
            Your goal is to help users (Clients or Employees/Admins) get an insurance quote.

            PERSONAS:
            1. **SELF-SERVICE (CLIENT)**: You are talking directly to the policyholder. Use their Client_ID from the context.
            2. **ASSISTED-SERVICE (STAFF)**: You are talking to an agent or admin. They are creating a quote for someone else. You MUST identify a client first.

            WORKFLOW FOR STAFF:
            1. If a client isn't selected, suggest using `list_recent_clients` or `search_clients(query)` to find a client.
            2. When displaying clients, use EXACTLY this format for a clickable list:
               - [Client Name](select-client:UUID:Client Name)
            3. Once a client is identified, wait for confirmation or use the selected one.
            4. Once a client is selected, IMMEDIATELY use `get_eligible_policies` to show available products for that client.

            CRITICAL:
            - ALWAYS use the IDs provided in the [SYSTEM CONTEXT VARIABLES].
            - Format client results as a clickable list: `[Name](select-client:UUID:Name)`
            - ALWAYS execute tools to get data. 
            - NEVER output Python code, JSON, or tool call syntax to the user.
            - Provide a natural language response based on the tool results.
            """,
            tools=[get_eligible_policies, update_client_profile, generate_insurance_quote, search_clients, list_recent_clients]
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
            from app.models.user import User as UserModel
            execution_user = db.query(UserModel).filter(UserModel.id == uuid.UUID(str(user_id))).first()
            
            user_role = execution_user.role if execution_user else "client"
            is_staff = user_role in ["super_admin", "company_admin", "manager", "agent"]
            
            # Context Variables for the Prompt
            ctx_vars = {
                "Company_ID": str(company_id),
                "User_ID": str(user_id),
                "User_Role": user_role
            }
            
            # If not staff, we must find the client profile linked to this user
            if not is_staff:
                client = (
                    db.query(Client)
                    .join(client_company, client_company.c.client_id == Client.id)
                    .filter(Client.user_id == uuid.UUID(str(user_id)))
                    .filter(client_company.c.company_id == uuid.UUID(str(company_id)))
                    .first()
                )
                
                if not client:
                     event_queue.enqueue_event(new_agent_text_message("I could not find your client profile. Please contact support."))
                     return
                ctx_vars["Client_ID"] = str(client.id)
                ctx_vars["Client_Name"] = f"{client.first_name} {client.last_name}"
            else:
                # For staff, we see if a client was already selected in history or if they are in the context
                target_client_id = context.metadata.get("target_client_id")
                
                # FALLBACK: Search history for "ID: <uuid>" selection pattern
                if not target_client_id:
                    for h in reversed(history):
                        if h["role"] == "user" and "ID:" in h.get("text", ""):
                            # Try to find a UUID in the selection message
                            found_ids = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', h.get("text", ""))
                            if found_ids:
                                target_client_id = found_ids[0]
                                print(f"DEBUG_AUTH: Rescued target_client_id from history: {target_client_id}")
                                break
                                
                if target_client_id:
                     ctx_vars["Target_Client_ID"] = str(target_client_id)
                     # Also try to find the name if possible to be helpful
                     tc = (
                         db.query(Client)
                         .join(client_company, client_company.c.client_id == Client.id)
                         .filter(Client.id == uuid.UUID(str(target_client_id)))
                         .filter(client_company.c.company_id == uuid.UUID(str(company_id)))
                         .first()
                     )
                     if tc:
                         ctx_vars["Target_Client_Name"] = f"{tc.first_name} {tc.last_name}"
            
            # 4. Construct Prompt with Context
            tenant_context_summary = build_tenant_context_summary(db, company_id)
            context_prompt = f"""
            
            {tenant_context_summary}
            
            [SYSTEM CONTEXT VARIABLES]
            {json.dumps(ctx_vars, indent=2)}
            
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
                    # For staff, we need to be careful about which ID is which
                    # But if the agent correctly outputs get_eligible_policies(target_client_id, company_id)
                    # and we catch it, we should use those.
                    
                    found_client_id = ctx_vars.get("Client_ID") or ctx_vars.get("Target_Client_ID")
                    
                    if not found_client_id and len(ids) >= 1:
                        # Fallback to first UUID in output if context is missing it
                        found_client_id = ids[0]
                    
                    if found_client_id and company_id:
                        tool_result_json = get_eligible_policies(str(found_client_id), str(company_id))
                        
                        try:
                            result_data = json.loads(tool_result_json)
                            if result_data.get("status") == "success":
                                p_list = result_data.get("eligible_policies", [])
                                # Format policies as clickable too
                                policy_list = "\n".join([f"- [**{p['name']}**](select-policy:{p['id']}:{p['name']}): {p['description']} (Premium: {p['estimated_premium']})" for p in p_list])
                                response_text = f"I've found the following eligible policies for the client:\n\n{policy_list}\n\nWhich one would you like to proceed with? (Click to select)"
                            elif result_data.get("status") == "missing_info":
                                missing = ", ".join(result_data.get("missing_fields", []))
                                response_text = f"To provide accurate policies, I need a bit more information about the client. Could you please provide their: {missing}?"
                            else:
                                response_text = f"I checked eligibility, but unfortunately: {result_data.get('message', 'No policies found.')}"
                        except Exception as e:
                            response_text = f"System: Tool execution failed: {str(e)}"
                    else:
                        response_text = "I need a selected client to check eligibility. Please search for a client first."

            # Check for list_recent_clients / search_clients to ensure clickable formatting
            if any(x in response_text for x in ["list_recent_clients", "search_clients"]) and "[" not in response_text:
                print("DEBUG: Potentially raw list output detected. Ensuring clickable format.")
                # This is a bit complex to fix raw output here, but instructions should handle it.
                # However, let's add a post-process if we see JSON-ish output in response_text
                if response_text.strip().startswith("[{") or response_text.strip().startswith("[ {\"id\""):
                    try:
                        data = json.loads(response_text)
                        if isinstance(data, list) and len(data) > 0 and "id" in data[0]:
                            clickable_list = "\n".join([f"- [{item.get('name', 'Client')}](select-client:{item['id']}:{item.get('name', 'Client')}) ({item.get('email', '')})" for item in data])
                            response_text = f"I found the following clients for you. Please click one to select:\n\n{clickable_list}"
                    except:
                        pass

            # --- SYNTHESIS ENFORCEMENT ---
            # If the model output code or JSON instead of a friendly response, we force a synthesis
            iterations = 0
            while any(x in response_text for x in ["def ", "import ", "print(", "{", "[{"]) and iterations < 2:
                print(f"DEBUG: Quote Agent leaked code/JSON. Forcing synthesis iteration {iterations+1}...")
                synthesis_prompt = f"The tools or system returned the following technical data or code. Please provide a clear, helpful, and friendly response for the user in natural language. DO NOT return any code, JSON, or Python snippets. If it is a list of clients, use the format: - [Name](select-client:UUID:Name)\n\nData: {response_text}"
                response_text = await self.agent.run(synthesis_prompt, google_api_key=context.metadata.get("google_api_key"))
                iterations += 1

            event_queue.enqueue_event(new_agent_text_message(response_text))
            
        except Exception as e:
            print(f"Quote Agent Error: {e}")
            event_queue.enqueue_event(new_agent_text_message(f"I encountered a system error: {str(e)}"))
        finally:
            db.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
