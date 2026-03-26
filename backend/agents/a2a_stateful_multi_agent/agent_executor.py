from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class StatefulMultiAgentExecutor(AgentExecutor):
    def __init__(self):
        # Emulating the stateful behavior of reference 8
        self.agent = Agent(
            name="customer_service_agent",
            model="gemini-2.0-flash",
            description="Agent that maintains state across transfers",
            instruction="""
            You are a helpful customer service agent.
            """,
            # sub_agents would be defined here
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Hello"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking the stateful transfer logic
        response_text = f"I am a stateful agent. I heard '{user_input}'."
        
        if "transfer" in user_input.lower():
             response_text += "\n\n(Transferring to specialist while maintaining context...)"
            
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
