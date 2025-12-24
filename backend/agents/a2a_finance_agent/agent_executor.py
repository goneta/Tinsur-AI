from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

class FinanceAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="finance_agent",
            model="gemini-2.0-flash",
            description="Agent that handles financial reports",
            instruction="""
            You are a Finance Agent.
            Generate reports and payroll info.
            """,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = "Generate Q4 Report"
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        # Mocking Finance logic
        report_data = "Revenue: $1,250,000.00\nExpenses: $450,000.00\nNet Profit: $800,000.00"
        
        response_text = f"Generating financial data for '{user_input}'.\n\n[Financial Report]\nPeriod: Q4 2024\n{report_data}"
        
        event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
