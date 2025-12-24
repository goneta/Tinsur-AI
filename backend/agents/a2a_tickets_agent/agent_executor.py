
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import create_support_ticket, get_ticket_status, list_active_tickets
import json

class TicketsAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="tickets_agent",
            model="gemini-3-pro-preview",
            description="Agent that manages support tickets for clients",
            instruction="""
            You are a Support Tickets Agent for InsurSaaS.
            Help users create, check status, or list their support tickets.
            Tools:
            - create_support_ticket: Use when user wants to report an issue. Ask for subject/description if not clear.
            - get_ticket_status: Use when user provides a ticket number (TKT-...).
            - list_active_tickets: Use when user wants to see their existing issues.
            ALWAYS confirm client_id and company_id are available in context.
            """,
            tools=[create_support_ticket, get_ticket_status, list_active_tickets]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        client_id = context.metadata.get("client_id")
        company_id = context.metadata.get("company_id")
        
        prompt = user_input
        if client_id and company_id:
            prompt = f"[Context: client_id={client_id}, company_id={company_id}] {user_input}"
        
        try:
            response_text = await self.agent.run(prompt, google_api_key=context.metadata.get("google_api_key"))
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Tickets Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
