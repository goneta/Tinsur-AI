
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import PolicyAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)


def main():
    skill = AgentSkill(
        id="create_policy",
        name="Create Policy",
        description="Create insurance policy",
        tags=["policy", "risk"],
        examples=["Create policy for quote X"],
    )

    agent_card = AgentCard(
        name="Policy Agent",
        description="Business Agent for Policies",
        url="http://localhost:8021/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=PolicyAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_policy_agent on port 8021")
    try:
        app = server.build()
        port = int(os.getenv("PORT", 8021))
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
    except BaseException as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR in Policy Agent: {e}")

if __name__ == "__main__":
    main()
