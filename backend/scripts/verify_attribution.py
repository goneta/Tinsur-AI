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

async def verify_attribution():
    print("🧪 Verifying Source Attribution (RAG) Integration...")
    print("=====================================================")
    
    executor = SupportAgentExecutor()
    
    # Query that should trigger a search in test_policy.pdf (vintage car)
    query = "What are the rules regarding engine modifications for vintage cars?"
    print(f"\n❓ Query: {query}")
    
    context = RequestContext(
        events=[MockEvent(type="user_text_message", text=query)],
        metadata={
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "client_id": "bf448f88-fde2-48f4-97eb-ba8d189b6c4e",
            "company_id": "1e47dd3a-413a-4257-9114-fd8eed222908"
        }
    )
    event_queue = EventQueue()
    
    try:
        await executor.execute(context, event_queue)
        
        if event_queue.events:
            response = event_queue.events[0]
            text = response.get("text", "") if isinstance(response, dict) else getattr(response, "text", "")
            print(f"🤖 Response:\n{text}")
            
            # Validation: Look for source filename or "Found in:"
            if "test_policy.pdf" in text or "Page" in text or "Found in" in text:
                print("\n✅ SUCCESS: Source attribution found in response!")
            else:
                print("\n❌ FAILURE: No source attribution found.")
        else:
            print("\n❌ FAILURE: No response received.")
            
    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_attribution())
