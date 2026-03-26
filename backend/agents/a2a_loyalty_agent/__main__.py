
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from .agent_executor import LoyaltyAgentExecutor
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

def main():
    agent_card = AgentCard(
        name="Loyalty Agent",
        description="Business Agent for Loyalty",
        url="http://localhost:8028/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )
    request_handler = DefaultRequestHandler(agent_executor=LoyaltyAgentExecutor(), task_store=InMemoryTaskStore())
    server = A2AStarletteApplication(http_handler=request_handler, agent_card=agent_card)
    print("Starting a2a_loyalty_agent on port 8028")
    port = int(os.getenv("PORT", 8028))
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
