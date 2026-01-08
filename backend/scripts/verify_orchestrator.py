import asyncio
import os
import sys

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from backend.agents.a2a_multi_agent.agent_executor import MultiAgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import AgentMessage
from app.core.config import settings

async def verify_routing():
    print("Initializing MultiAgentExecutor...")
    try:
        executor = MultiAgentExecutor()
    except Exception as e:
        print(f"FAILED to initialize executor: {e}")
        return

    # Test Case 1: Claims Routing
    print("\n[TEST 1] Testing 'I want to file a claim' routing...")
    response = await run_agent(executor, "I want to file a claim for a car accident.")
    if "claim" in response.lower() or "incident" in response.lower():
        print("✅ PASSED: Routed to Claims Agent (Response relevant)")
    else:
        print(f"❌ FAILED: Response was: {response}")

    # Test Case 2: Quote Routing
    print("\n[TEST 2] Testing 'Get me a quote' routing...")
    response = await run_agent(executor, "Get me a quote for auto insurance.")
    if "quote" in response.lower() or "policy" in response.lower():
        print("✅ PASSED: Routed to Quote Agent (Response relevant)")
    else:
        print(f"❌ FAILED: Response was: {response}")

    # Test Case 3: Telematics Routing
    print("\n[TEST 3] Testing 'Check my driving score' routing...")
    response = await run_agent(executor, "How is my driving score?")
    if "score" in response.lower() or "driving" in response.lower():
        print("✅ PASSED: Routed to Telematics Agent (Response relevant)")
    else:
        print(f"❌ FAILED: Response was: {response}")

async def run_agent(executor, message):
    queue = EventQueue()
    events = [AgentMessage(type="user_text_message", text=message)]
    
    # Mock Context
    context = RequestContext(
        events=events,
        metadata={
            "user_id": "test-user-id",
            "company_id": "test-company-id",
            "google_api_key": settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
        }
    )

    try:
        await executor.execute(context, queue)
        
        # Extract response
        for event in reversed(queue.events):
            # Handle Dict (from utils.py)
            if isinstance(event, dict):
                if event.get("type") == "agent_text_message":
                    return event.get("text") or event.get("content")
            # Handle Object
            elif getattr(event, "type", "") == "agent_text_message":
                 if hasattr(event, "text"):
                     return event.text
                 elif hasattr(event, "content"):
                     return event.content
        return "NO RESPONSE"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    asyncio.run(verify_routing())
