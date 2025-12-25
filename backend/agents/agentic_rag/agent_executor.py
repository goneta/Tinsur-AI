from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class AgenticRagAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="agentic_rag",
            model="gemini-2.0-flash",
            description="ADK-based Retrieval-Augmented Generation (RAG) agent",
            instruction="""
            You are a RAG specialist. Your responsibility is document retrieval, knowledge grounding, 
            and answering questions over internal and external data sources.
            Always cite your data when possible and ensure your answers are grounded in the provided context.
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
        company_id = context.metadata.get("company_id")
        
        # In a real implementation, we would call retrieval tools first.
        # Here we instruct the agent to simulate RAG logic if no tools are explicitly bound yet.
        rag_instruction = f"Search knowledge base for company_id: {company_id}. Ground your answer in retrieved documents."
        
        response_text = await self.agent.run(user_input, instruction=rag_instruction, google_api_key=google_api_key)
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
