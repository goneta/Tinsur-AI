import os
import sys
import uvicorn
from dotenv import load_dotenv
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
try:
    from agent_executor import MultiAiAgentsExecutor
except ImportError:
    from .agent_executor import MultiAiAgentsExecutor

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)


def main():
    skill = AgentSkill(
        id="orchestrate",
        name="Orchestrate",
        description="Main entry point",
        tags=["orchestrator", "main"],
        examples=["I need a quote", "File a claim"],
    )

    agent_card = AgentCard(
        name="Main Orchestrator Agent",
        description="Main Orchestrator (Replication of 17-multi-ai_agents)",
        url="http://localhost:33335/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=MultiAiAgentsExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_multi_ai_agents on port 33335")
    try:
        app = server.build()
        port = int(os.getenv("PORT", 33335))
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="debug")
    except BaseException as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR (BaseException): {e}")

if __name__ == "__main__":
    main()
