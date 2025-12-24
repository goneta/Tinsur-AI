from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class VoiceAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="voice_agent",
            model="gemini-2.0-flash",
            description="Agent that handles voice interactions",
            instruction="""
            You are a voice agent. You speak.
            """,
            # tools for voice I/O
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Hello"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking voice response logic
        response_text = f"I heard you say '{user_input}'. (Generating Voice Response...)"
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
