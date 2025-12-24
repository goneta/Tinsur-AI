from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from app.core.agent_client import AgentClient

def check_permission(permissions, role, scope, action):
    """Check if scope:action exists in permissions list or if user is super_admin."""
    if role == "super_admin":
        return True
    perm = f"{scope}:{action}"
    return perm in permissions

class MultiAiAgentsExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="orchestrator_agent",
            model="gemini-3-pro-preview",
            description="Main orchestrator for Insurance SaaS",
            instruction="""
            You are the main AI assistant for InsurSaaS.
            You can help with Quotes, Policies, Claims, and more.
            Delegate detailed work to specialists.
            """,
            # sub_agents would be configured here to point to other A2A agents
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        try:
            user_input = "Hello"
            if context.events:
                 for event in reversed(context.events):
                     if event.type == "user_text_message":
                         user_input = event.text
                         break
            
            # Extract User Context (passed from Chat Endpoint)
            metadata = context.metadata or {}
            user_id = metadata.get("user_id")
            user_role = metadata.get("user_role")
            permissions = metadata.get("permissions", [])
            google_api_key = metadata.get("google_api_key")
            
            # 1. Use Gemini to determine intent and routing
            agent_to_call = None
            reasoning = "Not specified"
            try:
                # Add context to the LLM call
                history = [{"role": "user", "content": user_input}]
                
                # Instruction for routing
                routing_instruction = f"""
                You are a routing specialist for InsurSaaS. 
                Based on the user input, decide which specialist agent to call.
                Available agents:
                - claims_agent: For claims, accidents, damage reporting.
                - quote_agent: For insurance premium calculations, new quotes.
                - policy_agent: For policy details, renewals, or viewing active policies.
                - support_agent: For general help or technical issues.
                - finance_agent: For financial reports, payments, and billing.
                - ocr_agent: For scanning documents or images.
                - tickets_agent: For support ticket management.
                - referrals_agent: For referral programs and tracking.
                - loyalty_agent: For loyalty points and rewards.
                - telematics_agent: For driving data and car tracking.
                - ml_agent: For machine learning model management.
                - document_agent: For secure document sharing and collaboration.
                - ocr_agent: For scanning documents or images.
                - voice_agent: For voice-related interactions.
                - rag_agent: For knowledge retrieval from documents.
                - mcp_agent: For using Model Context Protocol tools.
                - structured_outputs_agent: General data extraction into JSON format.
                - tool_agent: For web searching or using external tools.
                - memory_agent: For long-term memory, saving facts about the user, or retrieving past information.

                Return a JSON object: {{"agent": "agent_name", "reasoning": "why you chose this"}}
                If no specific agent matches, use {{"agent": null, "reasoning": "general greeting"}}
                """
                
                # We use the ADK Agent for the intelligence
                llm_response = await self.agent.run(user_input, instruction=routing_instruction, google_api_key=google_api_key)
                
                # Parse LLM response (assuming it returns JSON-like text)
                import json
                try:
                    # Clean the response if it contains markdown markers or extra text
                    cleaned_json = llm_response.replace("```json", "").replace("```", "").strip()
                    # If there's extra text before/after JSON, try to find the first '{' and last '}'
                    if "{" in cleaned_json and "}" in cleaned_json:
                        cleaned_json = cleaned_json[cleaned_json.find("{"):cleaned_json.rfind("}")+1]
                    
                    routing_decision = json.loads(cleaned_json)
                    agent_to_call = routing_decision.get("agent")
                    reasoning = routing_decision.get("reasoning", "")
                    print(f"LLM Routing Decision: {agent_to_call} ({reasoning})")
                except:
                    # Fallback to simple matching if LLM JSON is malformed
                    print("LLM returned non-JSON response, falling back to keyword matching")
                    if "quote" in llm_response.lower() or "quote" in user_input.lower(): agent_to_call = "quote_agent"
                    elif "claim" in user_input.lower(): agent_to_call = "claims_agent"
                    elif "policy" in user_input.lower(): agent_to_call = "policy_agent"

            except Exception as e:
                print(f"LLM Routing Error: {str(e)}")
                # Hard fallback to previous keyword logic for reliability
                if "quote" in user_input.lower(): agent_to_call = "quote_agent"
                elif "claim" in user_input.lower(): agent_to_call = "claims_agent"

            # 2. Specialist Communication
            if agent_to_call:
                if not check_permission(permissions, user_role, agent_to_call.replace("_agent", ""), "read"):
                    response_text = f"I'm sorry, you do not have permission to access the {agent_to_call.replace('_agent', '')} service."
                else:
                    try:
                        response_text = f"**[Intelligent Routing]**: {reasoning if 'reasoning' in locals() else 'Routing to specialist...'}\n"
                        
                        # Pass history to specialists via context
                        history = []
                        for event in context.events:
                            history.append({
                                "role": "user" if event.type == "user_text_message" else "assistant",
                                "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                                "type": event.type
                            })
                        metadata["history"] = history
                        
                        client = AgentClient()
                        agent_response = await client.send_message(
                            agent_to_call, 
                            user_input, 
                            context=metadata, 
                            api_key=google_api_key
                        )
                        
                        if "messages" in agent_response and agent_response["messages"]:
                            last_msg = agent_response["messages"][-1]
                            specialist_reply = last_msg.get("text") or last_msg.get("content") or str(last_msg)
                            
                            if "```json" in specialist_reply:
                                response_text += f"\n\n{specialist_reply}" 
                            else:
                                response_text += f"\n[Specialist Reply]: {specialist_reply}"
                        else:
                            response_text += f"\n[System]: Connected to {agent_to_call}, but received no text response."
                    except Exception as e:
                        response_text += f"\n[Error]: Failed to reach {agent_to_call}. Details: {str(e)}"
            else:
                # If no agent, let the LLM handle a direct reply
                response_text = await self.agent.run(user_input, google_api_key=google_api_key)
            
            event_queue.enqueue_event(new_agent_text_message(response_text))
            
        except Exception as e:
            # Catch-all to prevent 500 Internal Server Error
            import traceback
            error_msg = f"Orchestrator Critical Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg) # Goes to stdout of the agent process
            event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
