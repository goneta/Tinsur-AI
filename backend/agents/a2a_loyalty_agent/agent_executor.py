
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import get_loyalty_points, redeem_loyalty_points
import json

class LoyaltyAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="loyalty_agent",
            model="gemini-3-pro-preview", # Upgrade for better tool use
            description="Agent that manages loyalty points and rewards",
            instruction="""
            You are a Loyalty Agent for InsurSaaS.
            Use the provided tools to check client points balance or redeem rewards.
            ALWAYS ask for or confirm the client_id from the context metadata before performing actions.
            If the user asks about points, call get_loyalty_points.
            If they want to use points, call redeem_loyalty_points.
            """,
            tools=[get_loyalty_points, redeem_loyalty_points]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Add client_id to the prompt so the agent knows who it's dealing with
        client_id = context.metadata.get("client_id")
        prompt = user_input
        if client_id:
            prompt = f"[Context: client_id={client_id}] {user_input}"
        
        try:
            response_text = await self.agent.run(prompt, google_api_key=context.metadata.get("google_api_key"))
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Loyalty Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
