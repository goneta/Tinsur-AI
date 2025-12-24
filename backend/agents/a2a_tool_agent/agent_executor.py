from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from google.adk.tools import google_search

class ToolAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="tool_agent",
            model="gemini-2.0-flash",
            description="Tool agent that can search google",
            instruction="""
            You are a helpful assistant that can use the following tools:
            - google_search
            """,
            tools=[google_search],
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Hello" 
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        try:
            # Actually run the agent with tools
            response_text = await self.agent.run(user_input)
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Tool Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
