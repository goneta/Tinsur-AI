
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import list_active_models, get_model_insight
import json

class MLAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="ml_agent",
            model="gemini-2.0-flash",
            description="Agent that manages machine learning models and provides performance insights",
            instruction="""
            You are an ML Specialist for InsurSaaS.
            Help users understand the status and performance of deployed machine learning models.
            - list_active_models: Use to show all models.
            - get_model_insight: Use to get details on a specific model.
            """,
            tools=[list_active_models, get_model_insight]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        company_id = context.metadata.get("company_id")
        prompt = user_input
        if company_id:
            prompt = f"[Context: company_id={company_id}] {user_input}"
        
        try:
            response_text = await self.agent.run(prompt, google_api_key=context.metadata.get("google_api_key"))
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"ML Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
