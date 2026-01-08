
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from agents.a2a_telematics_agent.agent_executor import TelematicsAgentExecutor
    print("SUCCESS: Imported TelematicsAgentExecutor")
    
    agent = TelematicsAgentExecutor()
    print("SUCCESS: Instantiated TelematicsAgentExecutor")
    
except ImportError as e:
    print(f"FAILURE: ImportError - {e}")
except Exception as e:
    print(f"FAILURE: {e}")
