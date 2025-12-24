
import os
import pathlib

BASE_DIR = pathlib.Path("backend")

FILES = {
    "google/adk/__init__.py": "",
    "google/adk/agents/__init__.py": """
class Agent:
    def __init__(self, name, model, description, instruction, tools=None, sub_agents=None, **kwargs):
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.sub_agents = sub_agents or []
""",
    "a2a/__init__.py": "",
    "a2a/server/__init__.py": "",
    "a2a/server/agent_execution/__init__.py": """
class AgentExecutor:
    async def execute(self, context, event_queue):
        pass
    async def cancel(self, context, event_queue):
        pass
""",
    "a2a/server/agent_execution/context.py": """
class RequestContext:
    def __init__(self, events=None):
        self.events = events or []
""",
    "a2a/server/events/__init__.py": "",
    "a2a/server/events/event_queue.py": """
class EventQueue:
    def enqueue_event(self, event):
        print(f"Event Enqueued: {event}")
""",
    "a2a/utils.py": """
def new_agent_text_message(text):
    return {"type": "agent_text_message", "text": text}
""",
    "a2a/server/apps.py": """
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from app.middleware.agent_auth import AgentAuthMiddleware

class A2AStarletteApplication:
    def __init__(self, http_handler, agent_card):
        self.http_handler = http_handler
        self.agent_card = agent_card

    def build(self):
        async def handle_request(request):
            data = await request.json()
            # Wrap in minimal context/queue mock
            # Real implementation would be more complex
            response = await self.http_handler.handle(data)
            return JSONResponse(response)

        routes = [
            Route("/send-message", endpoint=handle_request, methods=["POST"])
        ]
        
        app = Starlette(routes=routes)
        app.add_middleware(AgentAuthMiddleware)
        return app
""",
    "a2a/server/request_handlers.py": """
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

class DefaultRequestHandler:
    def __init__(self, agent_executor, task_store):
        self.agent_executor = agent_executor
        self.task_store = task_store

    async def handle(self, data):
        # Unwrap message
        msg = data.get("message", {})
        msg_text = msg.get("text", "")
        
        # Create minimal context event
        event_obj = type('Event', (), {'type': 'user_text_message', 'text': msg_text})
        context = RequestContext(events=[event_obj])
        
        # Create queue to capture response
        responses = []
        class MockQueue:
            def enqueue_event(self, evt):
                responses.append(evt)
        
        await self.agent_executor.execute(context, MockQueue())
        
        # Return last response
        return {"messages": responses}
""",
    "a2a/server/tasks.py": """
class InMemoryTaskStore:
    pass
""",
    "a2a/types.py": """
class AgentCapabilities:
    pass

class AgentSkill:
    def __init__(self, id, name, description, tags, examples):
        pass

class AgentCard:
    def __init__(self, name, description, url, defaultInputModes, defaultOutputModes, skills, version, capabilities):
        pass
"""
}

def create_mocks():
    for path, content in FILES.items():
        full_path = BASE_DIR / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        print(f"Created {full_path}")

if __name__ == "__main__":
    create_mocks()
