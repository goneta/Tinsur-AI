import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
import json

app = FastAPI()

async def event_generator(message: str):
    """Yields events simulated as a stream."""
    words = message.split()
    for i, word in enumerate(words):
        # Simulate thinking/processing time
        await asyncio.sleep(0.5) 
        
        # Construct an event data payload
        data = {
            "type": "agent_text_chunk",
            "content": word + " "
        }
        
        # SSE Format: "data: <json>\n\n"
        yield f"data: {json.dumps(data)}\n\n"
        
    # Final event
    await asyncio.sleep(0.5)
    yield f"data: {json.dumps({'type': 'agent_text_final', 'content': ''})}\n\n"

@app.post("/send-message")
async def send_message(request: Request):
    """
    Accepts a message and streams the response back.
    """
    body = await request.json()
    message = body.get("message", {}).get("text", "Echo")
    
    return StreamingResponse(
        event_generator(f"Echoing: {message}"), 
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11000)
