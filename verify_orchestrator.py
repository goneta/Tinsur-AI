
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.agents.a2a_multi_ai_agents.agent_executor import MultiAiAgentsExecutor
    print("Successfully imported MultiAiAgentsExecutor")
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Syntax or other Error: {e}")
