
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from .agent_executor import TicketsAgentExecutor
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

def main():
    skill = AgentSkill(
        id="manage_tickets",
        name="Manage Tickets",
        description="Handle support tickets",
        tags=["support", "tickets"],
        examples=["I need help with my policy", "Create a support ticket"],
    )

    agent_card = AgentCard(
        name="Tickets Agent",
        description="Business Agent for Support Tickets",
        url="http://localhost:8026/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=TicketsAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_tickets_agent on port 8026")
    port = int(os.getenv("PORT", 8026))
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
