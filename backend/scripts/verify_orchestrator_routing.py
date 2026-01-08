import asyncio
import os
import sys

# 1. Setup Paths
# Need parent of 'backend' to be in path so 'import backend.agents...' works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# Need 'backend' itself in path for 'libs' resolution if needed by some relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Helper libs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../libs")))

# Force UTF-8 for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

from backend.agents.a2a_multi_agent.agent_executor import MultiAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

# Mock Event class
class MockEvent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

async def main():
    print("🤖 Initializing Orchestrator (MultiAgentExecutor)...")
    try:
        executor = MultiAgentExecutor()
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return

    print("✅ Orchestrator Initialized.")
    
    query = "What is the deductible for the Bronze Plan?"
    print(f"❓ Querying: {query}")
    
    # Create Mock Context
    event = MockEvent(type="user_text_message", text=query)
    context = RequestContext(
        events=[event],
        metadata={"google_api_key": os.getenv("GOOGLE_API_KEY")} # Pass API key for ADK
    )
    
    event_queue = EventQueue()
    
    print("⏳ Executing Orchestrator (this uses Gemini for routing)...")
    await executor.execute(context, event_queue)
    
    # Check response relative to previous verify script
    # The Orchestrator should delegate to SupportAgent, which returns the answer.
    # The Orchestrator receives that answer and usually just returns it or synthesizes final response.
    # In MultiAgentExecutor code: event_queue.enqueue_event(new_agent_text_message(response_text))
    
    found_answer = False
    
    if event_queue.events:
        for evt in event_queue.events:
            if isinstance(evt, dict):
                evt_text = evt.get("text", "")
                evt_type = evt.get("type", "")
            else:
                evt_text = getattr(evt, "text", "")
                evt_type = getattr(evt, "type", "")

            if evt_type == "agent_text_message":
                print("\n📝 Response:")
                try:
                    print(f"-- START RESPONSE --\n{evt_text}\n-- END RESPONSE --")
                except Exception as e:
                    print(f"-- START RESPONSE (REPR) --\n{repr(evt_text)}\n-- END RESPONSE --")
                if ("Bronze Plan" in evt_text or "deductible" in evt_text) and "$" in evt_text:
                    print("\n✅ Verification PASSED: Orchestrator routed to Support Agent + RAG info found.")
                    found_answer = True
                else:
                    print("\n⚠️ Verification WARNING: Response might be generic or routing failed.")
            else:
                print(f"Event: {evt_type}")
    else:
        print("❌ No events returned.")
        
    if not found_answer:
        # Final desperate debug: print the debug file itself
        print("\n🔎 --- DEBUG FILE CONTENT (First 2000 chars) ---")
        try:
            with open("backend/debug_orchestrator_all.txt", "r", encoding="utf-8") as f:
                print(f.read(2000))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
