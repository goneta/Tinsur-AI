from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
# Mocking MCP logic as we might not have a local MCP server running for this test
# But the structure mimics the reference

class McpAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="local_mcp_agent",
            model="gemini-2.0-flash",
            description="Agent that uses MCP tools",
            instruction="""
            You are an agent with access to MCP tools.
            Use them to answer user query.
            """,
            # mcp_servers=[...] # ADK configuration for MCP
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        company_id = context.metadata.get("company_id")
        
        # Mocking MCP execution
        response_text = f"Accessing MCP tools for company {company_id} regarding '{user_input}'.\n\n[MCP Tool Output]: Found relevant data from FS/SQLite for this tenant."
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
