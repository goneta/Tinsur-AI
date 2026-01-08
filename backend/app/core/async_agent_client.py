import httpx
import json
import asyncio
from typing import AsyncGenerator, Dict, Any

class AsyncAgentClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_message_stream(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sends a message and yields parsed JSON events from the SSE stream.
        """
        url = f"{self.base_url}/send-message"
        payload = {
            "message": {
                "type": "user_text_message",
                "text": message
            }
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=30.0) as response:
                async for line in response.aiter_lines():
                    decoded_line = line.strip()
                    if decoded_line.startswith("data:"):
                        json_str = decoded_line[5:].strip()
                        try:
                            yield json.loads(json_str)
                        except json.JSONDecodeError:
                            print(f"Failed to decode: {json_str}")

