import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import AdkBaseAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)

def main():
    skill = AgentSkill(
        id="base_reasoning",
        name="Base Reasoning",
        description="Foundational reasoning and task execution",
        tags=["reasoning", "base", "adk"],
        examples=["Solve this logic puzzle", "Explain the core concepts of ADK"],
    )

    agent_card = AgentCard(
        name="ADK Base Agent",
        description="Foundation reasoning and action agent",
        url="http://localhost:8033/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=AdkBaseAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    port = 8033
    print(f"Starting adk_base on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
