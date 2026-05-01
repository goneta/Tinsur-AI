import json
import logging
import uuid

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import (
    create_premium_policy_type,
    list_premium_policy_types,
    update_premium_policy_type,
    delete_premium_policy_type,
    create_eligibility_criteria,
    list_eligibility_criteria,
    update_eligibility_criteria,
    delete_eligibility_criteria,
    create_policy_service,
    list_policy_services,
    update_policy_service,
    delete_policy_service,
    get_company_dashboard_stats,
)

logger = logging.getLogger(__name__)


class AdminAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="admin_agent",
            model="gemini-2.0-flash",
            description="Agent that manages premium policies, eligibility criteria, policy services, and provides business analytics for insurance company administrators.",
            instruction="""
            You are the Tinsur.AI Admin Operations Agent.
            You help insurance company administrators manage their product catalog and business configuration.

            CAPABILITIES:
            1. **Premium Policy Management**: Create, list, update, and delete premium policy types (insurance products).
            2. **Eligibility Criteria**: Create, list, update, and delete eligibility rules that determine which clients qualify for which policies.
            3. **Policy Services**: Create, list, update, and delete add-on services/coverages that can be attached to premium policies.
            4. **Business Analytics**: Get dashboard statistics and KPIs for the company.

            WORKFLOW GUIDELINES:
            - When an admin asks to create a premium policy, first list existing criteria and services so they can be attached.
            - When creating eligibility criteria, explain the available fields: age, driving_license_years, accident_count, no_claims_years, vehicle_value, employment_status, annual_income, vehicle_age.
            - When creating criteria, explain operators: >, >=, <, <=, =, between (e.g., '18,65'), in (e.g., 'employed,self-employed').
            - Always confirm the details before creating records.
            - Use the company_id from the [SYSTEM CONTEXT VARIABLES].
            - Present results in a clear, formatted way.
            - For analysis requests, use get_company_dashboard_stats and provide insights.
            - When listing items, always display them in a user-friendly format with key details.
            - Be proactive in suggesting next steps (e.g., "Would you like to attach any services to this policy?" after creating a policy type).

            IMPORTANT:
            - ALWAYS use the Company_ID from context, never ask the user for it.
            - NEVER output raw JSON or code to the user. Always format results in natural language.
            - ALWAYS verify data before deletion operations and inform the user clearly.
            - Prices should be presented in the company's currency (typically FCFA/XOF).
            """,
            tools=[
                create_premium_policy_type,
                list_premium_policy_types,
                update_premium_policy_type,
                delete_premium_policy_type,
                create_eligibility_criteria,
                list_eligibility_criteria,
                update_eligibility_criteria,
                delete_eligibility_criteria,
                create_policy_service,
                list_policy_services,
                update_policy_service,
                delete_policy_service,
                get_company_dashboard_stats,
            ],
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # 1. Build History
        history = context.metadata.get("history", [])
        if not history and context.events:
            for event in context.events:
                history.append({
                    "role": "user" if event.type == "user_text_message" else "assistant",
                    "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                })

        # 2. Extract User Input from latest event
        user_input = ""
        if context.events:
            for event in reversed(context.events):
                if event.type == "user_text_message":
                    user_input = event.text
                    break

        if not user_input:
            return

        # 3. Resolve Context IDs and validate permissions
        company_id = context.metadata.get("company_id")
        user_id = context.metadata.get("user_id")
        user_role = context.metadata.get("user_role", "agent")

        if not company_id:
            event_queue.enqueue_event(new_agent_text_message("I cannot process admin operations without organization context."))
            return

        # Only allow admin roles
        if user_role not in ["super_admin", "company_admin", "manager"]:
            event_queue.enqueue_event(new_agent_text_message("Admin operations are restricted to administrators and managers. Your current role does not have sufficient permissions."))
            return

        # 4. Prepare Context Variables
        ctx_vars = {
            "Company_ID": str(company_id),
            "User_ID": str(user_id),
            "User_Role": user_role,
        }

        # 5. Build Context Prompt
        context_prompt = f"""
[SYSTEM CONTEXT VARIABLES]
{json.dumps(ctx_vars, indent=2)}

[CONVERSATION HISTORY]
"""
        for h in history:
            role = "User" if h["role"] == "user" else "Assistant"
            text = h.get("text") or h.get("content", "")
            context_prompt += f"{role}: {text}\n"

        context_prompt += f"\nUser: {user_input}"

        # 6. Execute Agent
        try:
            response_text = await self.agent.run(
                context_prompt,
                google_api_key=context.metadata.get("google_api_key"),
            )
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            logger.error(f"Admin Agent Error: {e}")
            event_queue.enqueue_event(new_agent_text_message(f"I encountered a system error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
