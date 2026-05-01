import json
import logging
import uuid

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from .tools import (
    list_draft_quotes,
    convert_quote_to_policy,
    list_active_policies,
    get_policy_details,
    cancel_policy,
)

logger = logging.getLogger(__name__)


class PolicyAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="policy_agent",
            model="gemini-2.0-flash",
            description="Agent that manages insurance policies - creating policies from quotes, viewing policy details, and managing policy lifecycle.",
            instruction="""
            You are the Tinsur.AI Policy Agent.
            You help users manage insurance policies throughout their lifecycle.

            CAPABILITIES:
            1. **List Draft Quotes**: Show quotes ready to be converted into policies.
            2. **Convert Quote to Policy**: Turn an accepted quote into an active insurance policy.
            3. **List Active Policies**: Show all active policies, optionally filtered by client.
            4. **Get Policy Details**: Show comprehensive details about a specific policy.
            5. **Cancel Policy**: Cancel an active policy with a reason.

            WORKFLOW FOR POLICY CREATION:
            1. When a user says "create a policy", first use `list_draft_quotes` to show available quotes.
            2. Present the quotes in a readable format with quote numbers and client names.
            3. When the user selects a quote, use `convert_quote_to_policy` with the quote number.
            4. Confirm the new policy details to the user.

            WORKFLOW FOR POLICY INQUIRY:
            1. When a user asks about "my policies" or a specific policy, use `list_active_policies` or `get_policy_details`.
            2. Present the information in a clear, human-readable format.

            IMPORTANT:
            - ALWAYS use the Company_ID and User_ID from [SYSTEM CONTEXT VARIABLES].
            - For client users, use the Client_ID from context to filter their policies.
            - NEVER output raw JSON or code to the user. Format everything in natural language.
            - Present policy numbers, dates, and amounts clearly.
            - Amounts should be displayed in the company's currency (typically FCFA/XOF).
            """,
            tools=[
                list_draft_quotes,
                convert_quote_to_policy,
                list_active_policies,
                get_policy_details,
                cancel_policy,
            ],
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        history = context.metadata.get("history", [])
        if not history and context.events:
            for event in context.events:
                history.append({
                    "role": "user" if event.type == "user_text_message" else "assistant",
                    "text": event.text if hasattr(event, "text") else getattr(event, "content", ""),
                })

        user_input = ""
        if context.events:
            for event in reversed(context.events):
                if event.type == "user_text_message":
                    user_input = event.text
                    break

        if not user_input:
            return

        company_id = context.metadata.get("company_id")
        user_id = context.metadata.get("user_id")
        user_role = context.metadata.get("user_role", "client")

        if not company_id or not user_id:
            event_queue.enqueue_event(new_agent_text_message("I cannot process your request without organization context."))
            return

        ctx_vars = {
            "Company_ID": str(company_id),
            "User_ID": str(user_id),
            "User_Role": user_role,
        }

        # If client, add their client_id for filtering
        client_id = context.metadata.get("client_id")
        if client_id:
            ctx_vars["Client_ID"] = str(client_id)

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

        try:
            response_text = await self.agent.run(
                context_prompt,
                google_api_key=context.metadata.get("google_api_key"),
            )
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            logger.error(f"Policy Agent Error: {e}")
            event_queue.enqueue_event(new_agent_text_message(f"I encountered a system error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
