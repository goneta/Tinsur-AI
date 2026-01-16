
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
try:
    from agent_executor import ClaimsAgentExecutor
except ImportError:
    from .agent_executor import ClaimsAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)


def main():
    skill = AgentSkill(
        id="process_claims",
        name="Process Claims",
        description="Handle insurance claims",
        tags=["claims", "fraud"],
        examples=["File a claim"],
    )

    agent_card = AgentCard(
        name="Claims Agent",
        description="Business Agent for Claims",
        url="http://localhost:33333/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ClaimsAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_claims_agent on port 33333")
    port = int(os.getenv("PORT", 33333))
    uvicorn.run(server.build(), host="127.0.0.1", port=port)

if __name__ == "__main__":
    main()
