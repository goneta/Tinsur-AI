
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import get_referral_info, create_referral_link
import json

class ReferralsAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="referrals_agent",
            model="gemini-3-pro-preview",
            description="Agent that manages insurance referrals and tracking",
            instruction="""
            You are a Referrals Agent for InsurSaaS.
            Help users manage their referrals.
            Use get_referral_info to check their status.
            Use create_referral_link to generate a new code.
            ALWAYS confirm client_id and company_id are available in context.
            """,
            tools=[get_referral_info, create_referral_link]
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
            event_queue.enqueue_event(new_agent_text_message(f"Referrals Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
