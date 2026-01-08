import asyncio
import sys
import os

# Add backend to path to import AsyncAgentClient
# Assuming we run from Tinsur.AI root
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.async_agent_client import AsyncAgentClient

async def main():
    # Assuming practice agent runs on port 11000
    client = AsyncAgentClient("http://localhost:11000")
    
    print("Sending message: 'Hello Streaming World'")
    print("--- Stream Start ---")
    
    try:
        async for event in client.send_message_stream("Hello Streaming World"):
            content = event.get("content", "")
            print(content, end="", flush=True)
            
        print("\n--- Stream End ---")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the practice agent is running: 'python backend/agents/a2a_streaming_practice/agent.py'")

if __name__ == "__main__":
    asyncio.run(main())
