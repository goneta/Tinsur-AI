
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from agents.a2a_finance_agent.agent_executor import FinanceAgentExecutor
    print("SUCCESS: Imported FinanceAgentExecutor")
    
    agent = FinanceAgentExecutor()
    print("SUCCESS: Instantiated FinanceAgentExecutor")
    
except ImportError as e:
    print(f"FAILURE: ImportError - {e}")
except Exception as e:
    print(f"FAILURE: {e}")
