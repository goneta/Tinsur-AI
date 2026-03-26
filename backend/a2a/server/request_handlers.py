from a2a.server.agent_execution.context import RequestContext
from google.adk.agents.context import google_api_key_var

class CapturedEventQueue:
    def __init__(self):
        self.events = []
    
    def enqueue_event(self, event):
        # Extract text/content for the API response
        content = getattr(event, "text", None) or getattr(event, "content", None) or str(event)
        self.events.append({
            "type": getattr(event, "type", "agent_text_message"),
            "text": content
        })

class DefaultRequestHandler:
    def __init__(self, agent_executor, task_store):
        self.agent_executor = agent_executor
        self.task_store = task_store

    async def handle(self, data):
        # Unwrap message
        msg = data.get("message", {})
        msg_text = msg.get("text", "")
        metadata = data.get("context", {})
        
        # Create minimal context event
        event_obj = type('Event', (), {'type': 'user_text_message', 'text': msg_text})
        context = RequestContext(events=[event_obj], metadata=metadata)
        
        # Create queue to capture response
        event_queue = CapturedEventQueue()
        
        # Set the context variable for the duration of this request
        token = google_api_key_var.set(metadata.get("google_api_key"))
        try:
            await self.agent_executor.execute(context, event_queue)
        except Exception as e:
            import traceback
            print(f"ERROR IN REQUEST HANDLER: {str(e)}")
            traceback.print_exc()
            event_queue.enqueue_event(type('Event', (), {'type': 'error', 'text': f"Execution Error: {str(e)}"}))
        finally:
            google_api_key_var.reset(token)
        
        # Return all captured events
        return {"messages": event_queue.events}
