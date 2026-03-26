from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class AdkLiveAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="adk_live",
            model="gemini-2.0-flash", # Or Gemini Live specific model if available
            description="Real-time multimodal agent (Voice, Vision, Text)",
            instruction="""
            You are a real-time multimodal agent built with ADK and Gemini Live.
            You handle live interactions, streaming inputs, and multimodal use cases.
            Specifically, you power the voice mode of the AI Agent Manager.
            Respond in a way that is natural for voice interaction: concise, friendly, and helpful.
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
        # In a real Live scenario, this would handle streaming chunks.
        # For this A2A implementation, we treat it as a multimodal request/response.
        response_text = await self.agent.run(user_input, google_api_key=google_api_key)
        
        # Prepend voice-specific tag if not present (simple sim)
        if not response_text.startswith("[Voice Mode]"):
            response_text = f"[Voice Mode]: {response_text}"
            
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
