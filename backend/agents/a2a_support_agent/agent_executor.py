from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class SupportAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="support_agent",
            model="gemini-2.0-flash",
            description="Agent that provides customer support",
            instruction="""
            You are a Support Agent.
            Help the customer.
            """,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "I need help"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking Support logic
        response_text = f"Hello! I am the Support Agent. I see you asked: '{user_input}'.\n\nHow can I assist you further? I can help with Quotes, Claims, or contacting a human agent."
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
