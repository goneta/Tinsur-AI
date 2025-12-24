
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import get_driving_stats, get_safety_recommendations
import json

class TelematicsAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="telematics_agent",
            model="gemini-3-pro-preview",
            description="Agent that analyzes usage-based insurance (UBI) driving data",
            instruction="""
            You are a Telematics Agent for InsurSaaS.
            Provide insights into driving behavior.
            - get_driving_stats: Get recent trip and score.
            - get_safety_recommendations: Get tips to improve score.
            ALWAYS confirm policy_id is available in context metadata.
            """,
            tools=[get_driving_stats, get_safety_recommendations]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        policy_id = context.metadata.get("policy_id")
        company_id = context.metadata.get("company_id")
        prompt = user_input
        
        context_str = []
        if policy_id: context_str.append(f"policy_id={policy_id}")
        if company_id: context_str.append(f"company_id={company_id}")
        
        if context_str:
            prompt = f"[Context: {', '.join(context_str)}] {user_input}"
        
        try:
            response_text = await self.agent.run(prompt, google_api_key=context.metadata.get("google_api_key"))
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Telematics Agent Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
