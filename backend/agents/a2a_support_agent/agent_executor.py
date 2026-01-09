from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

from .tools import (
    search_knowledge_base, 
    create_support_ticket, 
    get_user_policies, 
    get_user_payments, 
    get_user_claims,
    cancel_policy,
    schedule_callback,
    analyze_incident_image,
    automated_claim_registration,
    get_proactive_alerts,
    waive_late_fee
)

class SupportAgentExecutor(AgentExecutor):
    def __init__(self):
        # 1. Initialize Agent Definition with Tools
        self.agent = Agent(
            name="support_agent",
            model="gemini-2.0-flash",
            description="Agent that provides customer support using Knowledge Base, Ticket Escalation, and self-service actions",
            instruction="""
            You are the Tinsur.AI Support Specialist. 
            Your goal is to provide accurate, helpful, and empathetic assistance to our clients.
            
            1. PERSONALIZED DATA: For questions about policies, payments, or claims, 
               ALWAYS use a tool.
            
            2. MANDATORY SYNTHESIS: NEVER output raw tool output or JSON. 
               Summarize the results into a human-friendly response.
            
            3. TRANSPARENCY: When providing information from the knowledge base, 
               ALWAYS include the source and page/chunk information at the 
               end of your response (e.g., "Found in: test_policy.pdf, Page 2").
            
            4. ACTION: SELF-SERVICE:
               - To cancel a policy, MUST ask the user for a reason first.
               - To schedule a callback, ask for a preferred time and the topic.
            
            5. MULTI-MODAL CLAIMS:
               - If an incident is mentioned and an image path is provided ([IMAGE_PATH: ...]), 
                 ALWAYS use 'analyze_incident_image' first.
               - Summarize the assessment (severity, cost) and ask for confirmation.
               - If confirmed, use 'automated_claim_registration' to file the claim.
            
            6. INTELLIGENT CARE (PROACTIVE):
               - If '[PROACTIVE_ALERTS: ...]' is present, identify relevant issues 
                 (e.g., late payments) and offer help proactively.
               - Be empathetic. For a first-time late payment, you have the authority 
                 to offer to 'waive_late_fee'. Always confirm with the user first.
            
            7. OPTIMIZATION: Use the 'category' filter in 'search_knowledge_base' 
               whenever possible to improve speed and accuracy.
               Available categories: 'auto', 'general'.
            
            8. ESCALATION: Use 'create_support_ticket' if tools fail or if specifically requested.
            
            CONTEXT: Use the client_id and company_id provided.
            """,
            tools=[
                search_knowledge_base, 
                create_support_ticket, 
                get_user_policies, 
                get_user_payments, 
                get_user_claims,
                cancel_policy,
                schedule_callback,
                analyze_incident_image,
                automated_claim_registration,
                get_proactive_alerts,
                waive_late_fee
            ]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        user_image_path = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message" and not user_input:
                     user_input = event.text
                 elif event.type == "user_image_message" and not user_image_path:
                     user_image_path = getattr(event, "path", "") or event.get("path", "")
        
        if not user_input and not user_image_path:
            return

        client_id = context.metadata.get("client_id")
        company_id = context.metadata.get("company_id")
        
        prompt = user_input
        if user_image_path:
            prompt += f"\n[IMAGE_PATH: {user_image_path}]"

        if client_id and company_id:
            prompt = f"[Context: client_id={client_id}, company_id={company_id}] {prompt}"
            
            # Proactive Analysis (only on first user message typically, or periodically)
            # For simplicity, we check if there are few events or if this is a fresh prompt
            if len(context.events or []) <= 4:
                try:
                    alerts_json = get_proactive_alerts(client_id)
                    import json
                    alerts = json.loads(alerts_json)
                    if alerts:
                        prompt = f"[PROACTIVE_ALERTS: {alerts_json}] {prompt}"
                except Exception as e:
                    print(f"DEBUG: Failed to get proactive alerts: {str(e)}")

        try:
            # We pass the user query to the agent. 
            response_text = await self.agent.run(
                prompt, 
                google_api_key=context.metadata.get("google_api_key")
            )
            
            # Synthesis Fallback: If agent returns raw tool code, force a summarization
            iterations = 0
            while "tool_code" in response_text and iterations < 2:
                print(f"DEBUG: Agent returned raw tool code. Forcing synthesis iteration {iterations+1}...")
                synthesis_prompt = f"The tools returned the following data. Please provide a clear, helpful, and friendly summary of this information for the user in natural language. DO NOT return any code or JSON.\n\nData: {response_text}"
                response_text = await self.agent.run(
                    synthesis_prompt,
                    google_api_key=context.metadata.get("google_api_key")
                )
                iterations += 1

            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            print(f"⚠️  SupportAgent Execution Failed: {str(e)}")
            event_queue.enqueue_event(new_agent_text_message(
                "I'm sorry, I encountered an error while processing your request."
            ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass

