
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from agents.a2a_ml_agent.agent_executor import MLAgentExecutor
    print("SUCCESS: Imported MLAgentExecutor")
    
    agent = MLAgentExecutor()
    print("SUCCESS: Instantiated MLAgentExecutor")
    
except ImportError as e:
    print(f"FAILURE: ImportError - {e}")
except Exception as e:
    print(f"FAILURE: {e}")
