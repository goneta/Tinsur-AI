
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from agents.a2a_policy_agent.agent_executor import PolicyAgentExecutor
    print("SUCCESS: Imported PolicyAgentExecutor")
    
    agent = PolicyAgentExecutor()
    print("SUCCESS: Instantiated PolicyAgentExecutor")
    
except ImportError as e:
    print(f"FAILURE: ImportError - {e}")
except Exception as e:
    print(f"FAILURE: {e}")
