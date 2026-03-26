import asyncio
import os
import sys

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Ensure local libs is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../libs")))

# Force UTF-8 for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

# Fix: Import directly from a2a package which is in backend/
from agents.a2a_support_agent.agent_executor import SupportAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

# Mock Event class since it's missing in the backend checks
class MockEvent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

async def main():
    print("🤖 Initializing Support Agent...")
    try:
        executor = SupportAgentExecutor()
    except Exception as e:
        print(f"❌ Failed to initialize executor: {e}")
        return

    print("✅ Agent Initialized.")
    
    query = "What are the rules regarding engine modifications for vintage cars?"
    print(f"❓ Querying: {query}")
    
    # Create Mock Context
    event = MockEvent(type="user_text_message", text=query)
    context = RequestContext(
        events=[event],
        metadata={"google_api_key": os.getenv("GOOGLE_API_KEY")}
    )
    # The SupportAgentExecutor expects context to have these attributes (based on other files, or maybe it doesn't use them)
    # But let's stick to what we saw in the executor code: it iterates context.events.
    
    event_queue = EventQueue()
    
    await executor.execute(context, event_queue)
    
    # Check response (EventQueue is just a list wrapper in this codebase)
    if event_queue.events:
        for evt in event_queue.events:
            # The agent returns a dict from new_agent_text_message
            if isinstance(evt, dict):
                evt_type = evt.get("type")
                evt_text = evt.get("text")
            else:
                evt_type = evt.type
                evt_text = evt.text

            if evt_type == "agent_text_message":
                print("\n📝 Response:")
                print(evt_text)
                if "Bronze Plan" in evt_text or "deductible" in evt_text:
                    print("\n✅ Verification PASSED: Context retrieved.")
                else:
                    print("\n⚠️ Verification WARNING: Response might be generic.")
            else:
                print(f"Event: {evt_type}")
    else:
        print("❌ No events returned.")

if __name__ == "__main__":
    asyncio.run(main())
