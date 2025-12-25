from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class AdkA2ABaseAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="adk_a2a_base",
            model="gemini-2.0-flash",
            description="Agent specialized in Agent-to-Agent (A2A) communication",
            instruction="""
            You are an Agent-to-Agent (A2A) communication specialist built with Google ADK.
            Your role is to facilitate structured collaboration between agents within the AI Agent Manager mesh.
            You should ensure that requests between agents are clear, well-formatted, and contain all necessary context.
            """
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        google_api_key = context.metadata.get("google_api_key")
        
        # Invoke ADK Agent
        response_text = await self.agent.run(user_input, google_api_key=google_api_key)
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
