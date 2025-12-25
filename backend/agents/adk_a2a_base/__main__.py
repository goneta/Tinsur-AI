import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import AdkA2ABaseAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)

def main():
    skill = AgentSkill(
        id="a2a_communication",
        name="A2A Communication",
        description="Structured collaboration between agents",
        tags=["a2a", "coordination"],
        examples=["Coordinate between Agent A and Agent B"],
    )

    agent_card = AgentCard(
        name="ADK A2A Base Agent",
        description="Agent specialized for inter-agent communication",
        url="http://localhost:8034/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=AdkA2ABaseAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    port = 8034
    print(f"Starting adk_a2a_base on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
