
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from .agent_executor import TelematicsAgentExecutor
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

def main():
    agent_card = AgentCard(
        name="Telematics Agent",
        description="Business Agent for Telematics",
        url="http://localhost:8029/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )
    request_handler = DefaultRequestHandler(agent_executor=TelematicsAgentExecutor(), task_store=InMemoryTaskStore())
    server = A2AStarletteApplication(http_handler=request_handler, agent_card=agent_card)
    print("Starting a2a_telematics_agent on port 8029")
    port = int(os.getenv("PORT", 8029))
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
