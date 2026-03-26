from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class LoopAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="linkedin_post_agent",
            model="gemini-2.0-flash",
            description="Agent that improves posts in a loop",
            instruction="""
            You are a LinkedIn post enhancer.
            """,
            # loop configuration wrapped here
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Draft post regarding AI"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking loop logic
        response_text = f"Drafting post for '{user_input}'...\n\nIteration 1: Basic draft.\nIteration 2: Added emojis.\nIteration 3: Improved hook.\n\nFinal Output: 🚀 AI is changing the world! #AI #Tech"
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
