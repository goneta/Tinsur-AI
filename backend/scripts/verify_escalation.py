import asyncio
import os
import sys

# Setup Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../libs")))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

from backend.agents.a2a_support_agent.agent_executor import SupportAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

class MockEvent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

async def test_escalation():
    print("🚀 Testing Support Agent Escalation (Ticket Creation)...")
    
    executor = SupportAgentExecutor()
    
    # Simulate a request that requiring escalation
    query = "I have a complex question about a modified vintage car that isn't in your FAQ. I need to speak to a human."
    print(f"❓ Query: {query}")
    
    # Use real-ish IDs from DB
    client_id = "bf448f88-fde2-48f4-97eb-ba8d189b6c4e" 
    company_id = "1e47dd3a-413a-4257-9114-fd8eed222908"
    
    context = RequestContext(
        events=[MockEvent(type="user_text_message", text=query)],
        metadata={
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "client_id": client_id,
            "company_id": company_id
        }
    )
    
    event_queue = EventQueue()
    
    await executor.execute(context, event_queue)
    
    if event_queue.events:
        for evt in event_queue.events:
            text = evt.get("text", "") if isinstance(evt, dict) else getattr(evt, "text", "")
            print(f"\n📝 Response:\n{text}")
            if "TKT-" in text.upper():
                print("\n✅ SUCCESS: Ticket was created successfully!")
            else:
                print(f"\n❌ FAILURE: No ticket number found in response.")
                print(f"Full response was: {text}")
    else:
        print("❌ No response received.")

if __name__ == "__main__":
    asyncio.run(test_escalation())
