from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

from .tools import search_knowledge_base, create_support_ticket

class SupportAgentExecutor(AgentExecutor):
    def __init__(self):
        # 1. Initialize Agent Definition with Tools
        self.agent = Agent(
            name="support_agent",
            model="gemini-2.0-flash",
            description="Agent that provides customer support using Knowledge Base and Ticket Escalation",
            instruction="""
            You are a Support Agent for Tinsur.AI.
            Your job is to answer user questions about insurance policies, coverage, 
            claims procedures, and other general platform inquiries.
            
            1. ALWAYS use the 'search_knowledge_base' tool to find accurate information 
               before answering. 
            
            2. If the information is NOT found in the knowledge base, OR if the user 
               explicitly asks to speak to a human or needs complex help, you MUST 
               use the 'create_support_ticket' tool immediately to escalate.
            
            3. DO NOT just promise to create a ticket. Actually call the tool and 
               provide the resulting ticket number in your final response.
            
            ALWAYS confirm client_id and company_id are available in context before 
            creating a ticket.
            Keep your answers professional and concise.
            """,
            tools=[search_knowledge_base, create_support_ticket]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        if not user_input:
            return

        client_id = context.metadata.get("client_id")
        company_id = context.metadata.get("company_id")
        
        prompt = user_input
        if client_id and company_id:
            prompt = f"[Context: client_id={client_id}, company_id={company_id}] {user_input}"

        try:
            # We pass the user query to the agent. 
            response_text = await self.agent.run(
                prompt, 
                google_api_key=context.metadata.get("google_api_key")
            )
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            print(f"⚠️  SupportAgent Execution Failed: {str(e)}")
            event_queue.enqueue_event(new_agent_text_message(
                "I'm sorry, I encountered an error while processing your request."
            ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass

