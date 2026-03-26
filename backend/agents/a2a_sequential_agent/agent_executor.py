from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class SequentialAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="lead_qualification_agent",
            model="gemini-2.0-flash",
            description="Agent that runs steps sequentially",
            instruction="""
            You are a lead qualification agent.
            """,
            # sub_agents would be sequential here
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Hello"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking sequential logic
        response_text = f"I am a sequential agent.\n\nStep 1: Analyzed input '{user_input}'\nStep 2: Qualified as valid.\nStep 3: Stored in CRM."
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
