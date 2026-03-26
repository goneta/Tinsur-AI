from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class OcrAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="ocr_agent",
            model="gemini-2.5-flash",
            description="Agent that extracts text from documents",
            instruction="""
            You are an OCR agent.
            User sends a document (or description of one), you extract info.
            """,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        company_id = context.metadata.get("company_id")
        
        # Mock OCR logic
        response_text = f"Processing document request for company {company_id}: '{user_input}'...\n\n[OCR Result]\nInvoice #1234\nTotal: $500.00\nDate: 2024-12-14"
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
