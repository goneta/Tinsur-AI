import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'backend', 'agents', 'a2a_policy_agent'))

print("Testing Imports...")
try:
    from app.core.database import SessionLocal
    print("DB Import OK")
    
    from agents.a2a_policy_agent.agent_executor import PolicyAgentExecutor
    print("Agent Executor Import OK")
    
    executor = PolicyAgentExecutor()
    print("Agent Executor Init OK")

except Exception as e:
    import traceback
    print("FAILURE:")
    traceback.print_exc()
    sys.exit(1)

print("All Imports OK.")
