from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

# Define callbacks (mocked for wrapper)
def before_turn_callback(agent, turn_context):
    print("Before turn callback executed")

def after_turn_callback(agent, turn_context):
    print("After turn callback executed")

class CallbacksAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="before_after_agent",
            model="gemini-2.0-flash",
            description="Agent with callbacks",
            instruction="You are a helpful assistant.",
            # on_before_turn=before_turn_callback, # ADK logic
            # on_after_turn=after_turn_callback,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Fire "before" callback simulation
        before_turn_callback(self.agent, context)
        
        user_input = "Hello"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        response_text = f"I am an agent with callbacks. I heard '{user_input}'."
        event_queue.enqueue_event(new_agent_text_message(response_text))
        
        # Fire "after" callback simulation
        after_turn_callback(self.agent, context)

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
