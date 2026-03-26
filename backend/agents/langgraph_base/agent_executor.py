from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class LanggraphBaseAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="langgraph_base",
            model="gemini-2.0-flash",
            description="Base ReAct agent implemented with LangGraph (or simulating it)",
            instruction="""
            You are a workflow specialist. You support complex workflows, stateful reasoning, 
            and multi-step agent orchestration. 
            Maintain a clear state throughout the interaction and ensure each step logically follows the previous one.
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
        
        # Simulating stateful workflow
        # In a real LangGraph setup, we would load the 'graph' and run it.
        # Here we use the ADK agent to simulate the decision making of a graph.
        workflow_context = "Current state: Waiting for input. Step: 1 of N."
        response_text = await self.agent.run(user_input, instruction=f"Workflow Status: {workflow_context}", google_api_key=google_api_key)
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
