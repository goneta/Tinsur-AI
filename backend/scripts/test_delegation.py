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

async def test_delegation():
    print("🚀 Testing Direct Delegation to Support Agent Tool...")
    
    executor = SupportAgentExecutor()
    
    # Simulate a delegated request (as if from Manager)
    query = "The user is asking about the Bronze Plan deductible. Please provide the exact amount."
    print(f"❓ Query: {query}")
    
    context = RequestContext(
        events=[MockEvent(type="user_text_message", text=query)],
        metadata={"google_api_key": os.getenv("GOOGLE_API_KEY")}
    )
    
    event_queue = EventQueue()
    
    await executor.execute(context, event_queue)
    
    if event_queue.events:
        for evt in event_queue.events:
            text = evt.get("text", "") if isinstance(evt, dict) else getattr(evt, "text", "")
            print(f"\n📝 Response:\n{text}")
            if "$1,000" in text:
                print("\n✅ SUCCESS: Support Agent retrieved correct RAG info from tool.")
            else:
                print("\n❌ FAILURE: RAG info not found in response.")
    else:
        print("❌ No response received.")

if __name__ == "__main__":
    asyncio.run(test_delegation())
