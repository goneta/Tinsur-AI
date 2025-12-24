from datetime import datetime, date
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from app.services.accounting_service import AccountingService
from app.core.database import SessionLocal
import json

class FinanceAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="finance_agent",
            model="gemini-2.0-flash",
            description="Agent that handles financial reports and accounting data",
            instruction="""
            You are a Finance Agent for InsurSaaS.
            You can provide Profit & Loss (P&L) and Balance Sheet summaries.
            ALWAYS ask for the company_id if not provided in context.
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
        if not company_id:
            event_queue.enqueue_event(new_agent_text_message("Error: Missing company_id in context. I cannot access financial records."))
            return

        db = SessionLocal()
        try:
            service = AccountingService(db)
            input_lower = user_input.lower()
            
            if "profit" in input_lower or "p&l" in input_lower or "revenue" in input_lower:
                # Get YTD P&L
                end_date = datetime.now()
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0)
                pl = service.get_profit_loss(company_id, start_date, end_date)
                
                response = (f"Financial Summary (P&L - YTD) for Company {company_id}:\n"
                            f"- Total Revenue: {pl['total_revenue']}\n"
                            f"- Total Expenses: {pl['total_expenses']}\n"
                            f"- Net Profit: {pl['net_profit']}\n\n"
                            "Would you like a breakdown of specific accounts?")
            elif "balance" in input_lower or "asset" in input_lower:
                bs = service.get_balance_sheet(company_id, datetime.now())
                response = (f"Financial Summary (Balance Sheet) for Company {company_id}:\n"
                            f"- Total Assets: {bs['total_assets']}\n"
                            f"- Total Liabilities: {bs['total_liabilities']}\n"
                            f"- Total Equity: {bs['total_equity']}\n\n"
                            "Assets equals Liabilities + Equity? " + ("Yes" if (bs['total_assets'] == bs['total_liabilities'] + bs['total_equity']) else "No"))
            else:
                response = "I can provide Profit & Loss or Balance Sheet summaries. Which would you like to see?"
            
            event_queue.enqueue_event(new_agent_text_message(response))
        finally:
            db.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
