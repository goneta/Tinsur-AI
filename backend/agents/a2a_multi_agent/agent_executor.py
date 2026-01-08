from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent

# Import real backend agents
# Adapting imports assuming we are running from backend root or these modules are in python path
try:
    from backend.agents.a2a_claims_agent.agent_executor import ClaimsAgentExecutor
    from backend.agents.a2a_policy_agent.agent_executor import PolicyAgentExecutor
    from backend.agents.a2a_quote_agent.agent_executor import QuoteAgentExecutor
    from backend.agents.a2a_telematics_agent.agent_executor import TelematicsAgentExecutor
    from backend.agents.a2a_finance_agent.agent_executor import FinanceAgentExecutor
    from backend.agents.a2a_support_agent.agent_executor import SupportAgentExecutor
    from backend.agents.a2a_document_agent.agent_executor import DocumentAgentExecutor
except ImportError:
    # Fallback for different running contexts (e.g. inside agents dir)
    import sys
    import os
    # Add parent dir to path if needed for siblings
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    from backend.agents.a2a_claims_agent.agent_executor import ClaimsAgentExecutor
    from backend.agents.a2a_policy_agent.agent_executor import PolicyAgentExecutor
    from backend.agents.a2a_quote_agent.agent_executor import QuoteAgentExecutor
    from backend.agents.a2a_telematics_agent.agent_executor import TelematicsAgentExecutor
    from backend.agents.a2a_finance_agent.agent_executor import FinanceAgentExecutor
    from backend.agents.a2a_support_agent.agent_executor import SupportAgentExecutor
    from backend.agents.a2a_document_agent.agent_executor import DocumentAgentExecutor

class MultiAgentExecutor(AgentExecutor):
    def __init__(self):
        # Initialize sub-agents
        self.claims = ClaimsAgentExecutor()
        self.policy = PolicyAgentExecutor()
        self.quote = QuoteAgentExecutor()
        self.telematics = TelematicsAgentExecutor()
        self.finance = FinanceAgentExecutor()
        self.support = SupportAgentExecutor()
        self.document = DocumentAgentExecutor()
        
        # Create the Manager Agent with sub-agents
        self.agent = Agent(
            name="manager_agent",
            model="gemini-2.0-flash",
            description="Manager agent that routes user requests to specialized insurance agents",
            instruction="""
            You are the Tinsur.AI Manager Agent.
            Your job is to route user requests to the appropriate specialist agent.
            
            - If the user wants to check a claim status, file a claim, or asks about fraud, delegate to the 'claims_agent'.
            - If the user wants to create a policy, manage policies, or ask about coverage details, delegate to the 'policy_agent'.
            - If the user wants to get a quote, check prices, or create a new quote, delegate to the 'quote_agent'.
            - If the user asks about driving behavior, UBI scores, safety tips, or trips, delegate to the 'telematics_agent'.
            - If the user asks about financial reports, P&L, balance sheets, or accounting, delegate to the 'finance_agent'.
            - If the user needs help, support, or has general questions about the platform, delegate to the 'support_agent'.
            - If the user wants to generate, share, or revoke documents (agreements, slips), delegate to the 'document_agent'.
            
            If the request is general (e.g., 'Hello'), you can answer directly.
            """,
            sub_agents=[
                self.claims.agent, 
                self.policy.agent, 
                self.quote.agent, 
                self.telematics.agent,
                self.finance.agent,
                self.support.agent,
                self.document.agent
            ]
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        if not user_input:
            return

        try:
            # Pass metadata (context) down to sub-agents via the prompt or ADK context injection
            # The ADK Agent.run() handles sub-agent delegation automatically based on instructions.
            # We just need to ensure the sub-agents have access to tools/context if they rely on it.
            # In this ADK version, we pass the prompt and let the manager decide.
            
            # Note: For real context propagation (user_id, company_id) to sub-agents, 
            # we rely on the sub-agents' own execution logic if the ADK calls them directly 
            # or if we were manually routing. 
            # Since we are using `sub_agents=[]` in ADK, the ADK handles the routing loop.
            
            # We pass context.metadata as tool_config or bind it if supported, 
            # but for now we append context to the prompt if needed, similar to TelematicsAgent.
            # However, the ADK's multi-agent routing usually handles the conversation flow.
            
            response_text = await self.agent.run(user_input, google_api_key=context.metadata.get("google_api_key"))
            
            event_queue.enqueue_event(new_agent_text_message(response_text))
            
        except Exception as e:
            event_queue.enqueue_event(new_agent_text_message(f"Orchestrator Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
