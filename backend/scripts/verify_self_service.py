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

async def verify_self_service():
    print("🧪 Verifying Self-Service Actions...")
    print("======================================")
    
    executor = SupportAgentExecutor()
    
    # We'll use Ken Adams
    client_id = "bf448f88-fde2-48f4-97eb-ba8d189b6c4e" 
    company_id = "1e47dd3a-413a-4257-9114-fd8eed222908"
    
    # 1. Test Callback Scheduling
    print("\n🔹 Test 1: Scheduling a Callback")
    query1 = "Can I schedule a callback for tomorrow at 2 PM to talk about my premium increase?"
    print(f"❓ Query: {query1}")
    
    context1 = RequestContext(
        events=[MockEvent(type="user_text_message", text=query1)],
        metadata={
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "client_id": client_id,
            "company_id": company_id
        }
    )
    event_queue1 = EventQueue()
    await executor.execute(context1, event_queue1)
    
    if event_queue1.events:
        event = event_queue1.events[0]
        text = event.get("text", "") if isinstance(event, dict) else getattr(event, "text", "")
        print(f"🤖 Response: {text[:200]}...")
        if "scheduled" in text.lower() or "CBK-" in text:
            print("✅ SUCCESS: Callback scheduled!")
        else:
            print("❌ FAILURE: Callback not scheduled correctly.")

    # 2. Test Policy Cancellation
    print("\n🔹 Test 2: Canceling a Policy")
    # First, let's list policies to get a real one
    # But for the test, we can just say "Cancel my policy POL-XXXXX because I sold the car"
    # Actually, the agent might ask "Which policy?" if we don't specify.
    # Let's try a direct request.
    query2 = "I want to cancel my policy POL-C6C30D42 because I sold the vehicle."
    print(f"❓ Query: {query2}")
    
    context2 = RequestContext(
        events=[MockEvent(type="user_text_message", text=query2)],
        metadata={
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "client_id": client_id,
            "company_id": company_id
        }
    )
    event_queue2 = EventQueue()
    await executor.execute(context2, event_queue2)
    
    if event_queue2.events:
        event = event_queue2.events[0]
        text = event.get("text", "") if isinstance(event, dict) else getattr(event, "text", "")
        print(f"🤖 Full Response:\n{text}")
        if "canceled" in text.lower():
            print("✅ SUCCESS: Policy cancel tool invoked!")
        else:
            print("❌ FAILURE: Policy not canceled correctly.")

if __name__ == "__main__":
    asyncio.run(verify_self_service())
