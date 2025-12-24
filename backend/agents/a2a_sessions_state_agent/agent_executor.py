from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class SessionAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="question_answering_agent",
            model="gemini-2.0-flash",
            description="Agent that remembers your name",
            instruction="""
            You are a helpful assistant.
            If the user tells you their name, remember it for the session.
            If the user asks 'What is my name?', tell them the name you remember.
            """,
        )
        # Emulating session storage for the wrapper
        self.sessions = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Hello"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Simple session logic simulation
        # context.session_id would be available in real A2A
        session_id = getattr(context, 'session_id', 'default_session')
        
        # We would pass this session_id to ADK agent
        # response = await self.agent.generate_response(user_input, session_id=session_id)
        
        # Mock logic
        if "my name is" in user_input.lower():
            name = user_input.split("is")[-1].strip()
            self.sessions[session_id] = name
            response_text = f"Nice to meet you, {name}!"
        elif "what is my name" in user_input.lower():
            name = self.sessions.get(session_id, "unknown")
            if name != "unknown":
                response_text = f"Your name is {name}."
            else:
                response_text = "I don't know your name yet."
        else:
            response_text = f"I heard: {user_input}"
            
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
