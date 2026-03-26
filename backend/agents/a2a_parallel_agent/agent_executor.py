from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class ParallelAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="system_monitor_agent",
            model="gemini-2.0-flash",
            description="Agent that runs steps in parallel",
            instruction="""
            You are a system monitor.
            """,
            # sub_agents would be parallel here
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Status check"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking parallel logic
        response_text = f"Running checks in parallel for '{user_input}'...\n\n- DB: OK\n- API: OK\n- Cache: OK\n\nAll systems nominal."
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
