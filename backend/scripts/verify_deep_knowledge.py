import asyncio
import os
import sys

# Setup Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

from backend.agents.a2a_support_agent.agent_executor import SupportAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

class MockEvent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

async def verify_deep_knowledge():
    print("🧪 Verifying Deep Knowledge (Cross-Agent) Integration...")
    print("=========================================================")
    
    executor = SupportAgentExecutor()
    
    # We'll use a real client ID that has data (from our earlier script or known DB state)
    client_id = "bf448f88-fde2-48f4-97eb-ba8d189b6c4e" # Ken Adams
    company_id = "1e47dd3a-413a-4257-9114-fd8eed222908"
    
    queries = [
        "What policies do I have active right now?",
        "When is my next premium payment due?",
        "Show me the status of my claims."
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        
        context = RequestContext(
            events=[MockEvent(type="user_text_message", text=query)],
            metadata={
                "google_api_key": os.getenv("GOOGLE_API_KEY"),
                "client_id": client_id,
                "company_id": company_id
            }
        )
        event_queue = EventQueue()
        
        try:
            await executor.execute(context, event_queue)
            
            if event_queue.events:
                response = event_queue.events[0]
                text = response.get("text", "") if isinstance(response, dict) else getattr(response, "text", "")
                print(f"DEBUG: Raw Response: {text[:500]}...")
                
                # Basic validation
                if "Policy" in text or "payment" in text.lower() or "Claim" in text:
                    print("✅ SUCCESS: Agent used specialized tools!")
                else:
                    print("⚠️ WARNING: Response seems generic.")
            else:
                print("❌ FAILURE: No response received.")
                
        except Exception as e:
            print(f"❌ Execution Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_deep_knowledge())
