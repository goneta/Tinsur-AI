
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import LiteLlmAgentExecutor
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

def main():
    skill = AgentSkill(
        id="dad_jokes",
        name="Dad Jokes",
        description="Tell a dad joke",
        tags=["jokes", "fun"],
        examples=["Tell me a joke"],
    )

    agent_card = AgentCard(
        name="LiteLLM Dad Joke Agent",
        description="Agent using LiteLLM (Replication of 3-litellm-agent)",
        url="http://localhost:8003/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=LiteLlmAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_litellm_agent on port 8003")
    uvicorn.run(server.build(), host="0.0.0.0", port=8003)

if __name__ == "__main__":
    main()
