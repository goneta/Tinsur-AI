
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import BasicAgentExecutor
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

def main():
    skill = AgentSkill(
        id="basic_greeting",
        name="Greet",
        description="Return a greeting",
        tags=["greeting", "basic"],
        examples=["Hello", "Hi"],
    )

    agent_card = AgentCard(
        name="Basic Agent",
        description="A simple agent that returns a greeting (Replication of 1-basic-agent)",
        url="http://localhost:8001/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=BasicAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_basic_agent on port 8001")
    uvicorn.run(server.build(), host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()
