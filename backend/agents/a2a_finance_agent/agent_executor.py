from datetime import datetime, date
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from app.services.accounting_service import AccountingService
from app.core.database import SessionLocal
from app.core.security_context import SecurityService
from .tools import (
    get_financial_summary,
    get_claims_analysis,
    get_client_portfolio_analysis,
    get_ai_usage_report
)
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class FinanceAgentExecutor(AgentExecutor):
    def __init__(self):
        # Define tools based on role-based access
        tools = [
            get_financial_summary,
            get_claims_analysis,
            get_client_portfolio_analysis,
            get_ai_usage_report,
        ]

        self.agent = Agent(
            name="finance_agent",
            model="gemini-2.0-flash",
            description="Agent that handles financial reports, analytics, and reporting with role-based access",
            instruction="""
            You are a Finance Agent for InsurSaaS with role-based reporting capabilities.

            ROLE-BASED CAPABILITIES:
            - super_admin/company_admin: Full financial reports, all KPIs, claims analysis, AI usage, client portfolios
            - manager: Team performance, claims analysis, client portfolio overview
            - agent: Client-specific portfolio analysis only
            - client: Their own policy portfolio summary only

            AVAILABLE TOOLS:
            1. get_financial_summary(company_id, period_days): KPIs, premiums, claims, net revenue, loss ratios
            2. get_claims_analysis(company_id): Claims status breakdown, fraud flags, risk analysis
            3. get_client_portfolio_analysis(company_id, client_id=None): Client-specific or company-wide portfolio analysis
            4. get_ai_usage_report(company_id, period_days): AI agent usage, credits consumed, trends

            INSTRUCTIONS:
            - ALWAYS get the user's role from context (user_role) to determine which reports they can access
            - ALWAYS verify company_id is in context before making any queries
            - Provide helpful context about what each metric means
            - For clients, only show their own portfolio (restrict by client_id)
            - Offer to drill deeper or compare periods after initial reports
            - Be conversational and proactive with follow-up insights
            """,
            tools=tools,
        )

    def _get_user_role(self, context: RequestContext) -> str:
        """Extract user role from context metadata."""
        return context.metadata.get("user_role", "client").lower()

    def _check_role_permissions(self, role: str, report_type: str) -> bool:
        """Check if user role has permission for report type."""
        role_permissions = {
            "super_admin": ["financial_summary", "claims_analysis", "portfolio_analysis", "ai_usage"],
            "company_admin": ["financial_summary", "claims_analysis", "portfolio_analysis", "ai_usage"],
            "manager": ["claims_analysis", "portfolio_analysis"],
            "agent": ["portfolio_analysis"],
            "client": ["own_portfolio"],
        }

        allowed = role_permissions.get(role, [])
        return report_type in allowed

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        history = context.metadata.get("history", [])

        # Build history from context events if not already present
        if not history and context.events:
            for event in context.events:
                history.append({
                    "role": "user" if event.type == "user_text_message" else "assistant",
                    "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                    "type": event.type
                })

        user_input = history[-1]["text"] if history else ""

        try:
            company_id = context.metadata.get("company_id")
            user_id = context.metadata.get("user_id")
            user_role = self._get_user_role(context)
            client_id = context.metadata.get("client_id")  # For client-specific queries

            # Validation
            if not company_id:
                event_queue.enqueue_event(
                    new_agent_text_message(
                        "Error: Missing company_id in context. I cannot access financial records."
                    )
                )
                return

            db = SessionLocal()
            try:
                # Security Check: Verify user permissions
                if user_id:
                    security = SecurityService(db)
                    if not security.has_permission(uuid.UUID(user_id), "report", "read"):
                        event_queue.enqueue_event(
                            new_agent_text_message(
                                "Permission Denied: You do not have access to financial reports."
                            )
                        )
                        return

                # Parse user input and determine report type
                input_lower = user_input.lower()

                service = AccountingService(db)

                # Determine what the user is asking for
                report_type = None
                if any(word in input_lower for word in ["profit", "p&l", "revenue", "underwriting", "net"]):
                    report_type = "financial_summary"
                elif any(word in input_lower for word in ["claim", "fraud", "risk", "settlement"]):
                    report_type = "claims_analysis"
                elif any(word in input_lower for word in ["portfolio", "client", "policy", "coverage"]):
                    report_type = "portfolio_analysis"
                elif any(word in input_lower for word in ["ai usage", "credit", "agent"]):
                    report_type = "ai_usage"
                elif any(word in input_lower for word in ["balance", "asset", "liability", "equity"]):
                    report_type = "balance_sheet"

                # Check permissions
                if report_type and not self._check_role_permissions(user_role, report_type):
                    event_queue.enqueue_event(
                        new_agent_text_message(
                            f"Permission Denied: Your role '{user_role}' does not have access to {report_type} reports."
                        )
                    )
                    return

                # Build context-aware response based on role
                context_info = f"""
User Role: {user_role}
Company ID: {company_id}
Can access: {', '.join(context.metadata.get('user_role', 'client').lower() in ['super_admin', 'company_admin'] and ['financial_summary', 'claims_analysis', 'portfolio_analysis', 'ai_usage'] or user_role == 'manager' and ['claims_analysis', 'portfolio_analysis'] or user_role == 'agent' and ['portfolio_analysis'] or ['own_portfolio'])}
"""

                # Execute agent with tools and context
                response = await self.agent.run(
                    user_input,
                    context={
                        "company_id": company_id,
                        "user_role": user_role,
                        "client_id": client_id,
                        "context_info": context_info,
                        "history": history,
                    }
                )

                event_queue.enqueue_event(new_agent_text_message(str(response)))

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Finance agent error: {str(e)}", exc_info=True)
            event_queue.enqueue_event(
                new_agent_text_message(f"Error processing financial report: {str(e)}")
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
