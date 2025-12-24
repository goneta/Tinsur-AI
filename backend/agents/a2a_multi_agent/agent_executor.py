from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

# Mock sub-agents for the wrapper if we can't import the exact structure
# or if we want to contain it all in one file for the A2A wrapper
writer_agent = Agent(
    name="writer",
    model="gemini-2.0-flash",
    description="Writer agent",
    instruction="You are a writer. Write short stories.",
)

reviewer_agent = Agent(
    name="reviewer",
    model="gemini-2.0-flash",
    description="Reviewer agent",
    instruction="You are a reviewer. Review stories for clarity.",
)

class MultiAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="manager_agent",
            model="gemini-2.0-flash",
            description="Manager agent that delegates to writer and reviewer",
            instruction="""
            You are a manager.
            If the user asks to write a story, delegate to the writer.
            If the user asks to review a story, delegate to the reviewer.
            """,
            # sub_agents=[writer_agent, reviewer_agent] # Abstracted for ADK
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Write a story"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mock delegation logic
        if "write" in user_input.lower():
            # Real ADK would handle delegation automatically if configured
            # response = await self.agent.generate_response(user_input)
            response_text = "I'll ask the writer.\n\nWriter says: Once upon a time..."
        elif "review" in user_input.lower():
            response_text = "I'll ask the reviewer.\n\nReviewer says: The story looks good!"
        else:
            response_text = "I can manage writing and reviewing stories."
            
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
