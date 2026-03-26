
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
