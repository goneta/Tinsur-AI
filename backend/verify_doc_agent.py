
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from agents.a2a_document_agent.agent_executor import DocumentAgentExecutor
    print("SUCCESS: Imported DocumentAgentExecutor")
    
    # Try instantiation (mocking context might be needed if __init__ does heavy lifting, but it looks lightweight)
    agent = DocumentAgentExecutor()
    print("SUCCESS: Instantiated DocumentAgentExecutor")
    
except ImportError as e:
    print(f"FAILURE: ImportError - {e}")
except Exception as e:
    print(f"FAILURE: {e}")
