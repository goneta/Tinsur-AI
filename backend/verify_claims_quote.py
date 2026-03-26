
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from agents.a2a_claims_agent.agent_executor import ClaimsAgentExecutor
    print("SUCCESS: Imported ClaimsAgentExecutor")
    agent = ClaimsAgentExecutor()
    print("SUCCESS: Instantiated ClaimsAgentExecutor")
except Exception as e:
    print(f"FAILURE (Claims): {e}")

try:
    from agents.a2a_quote_agent.agent_executor import QuoteAgentExecutor
    print("SUCCESS: Imported QuoteAgentExecutor")
    agent = QuoteAgentExecutor()
    print("SUCCESS: Instantiated QuoteAgentExecutor")
except Exception as e:
    print(f"FAILURE (Quote): {e}")
