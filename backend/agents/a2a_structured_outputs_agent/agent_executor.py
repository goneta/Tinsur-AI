from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from pydantic import BaseModel, Field

class Email(BaseModel):
    subject: str = Field(description="The subject of the email")
    body: str = Field(description="The body of the email")
    spam_score: int = Field(description="The spam score of the email (0-100)")

class StructuredAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="email_agent",
            model="gemini-2.0-flash",
            description="Email agent",
            instruction="""
            You are a helpful assistant that generates emails. 
            Rank the spam score of the email from 0 to 100.
            """,
            output_type=Email,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Write an email"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        try:
            # Actually run the agent with structured output
            email_obj = await self.agent.run(user_input)
            
            if isinstance(email_obj, Email):
                response_text = f"Subject: {email_obj.subject}\n\n{email_obj.body}\n\n(Spam Score: {email_obj.spam_score})"
            else:
                response_text = str(email_obj)
                
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Structured Output Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
