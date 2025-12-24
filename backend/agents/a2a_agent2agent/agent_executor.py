from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class AgentToAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="connector_agent",
            model="gemini-2.0-flash",
            description="Agent that connects to others",
            instruction="""
            You are a connector agent.
            """,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Hello"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking A2A communication
        response_text = f"I am ready to connect to other agents. Received: '{user_input}'"
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
