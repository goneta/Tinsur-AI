
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import QuoteAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)


def main():
    skill = AgentSkill(
        id="generate_quote",
        name="Generate Quote",
        description="Calculate insurance quote",
        tags=["quote", "premium"],
        examples=["Quote for car insurance"],
    )

    agent_card = AgentCard(
        name="Quote Agent",
        description="Business Agent for Quotes",
        url="http://localhost:8020/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=QuoteAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_quote_agent on port 8020")
    try:
        app = server.build()
        port = int(os.getenv("PORT", 8020))
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
    except BaseException as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR in Quote Agent: {e}")

if __name__ == "__main__":
    main()
