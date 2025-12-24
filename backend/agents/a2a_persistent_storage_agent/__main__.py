import os
from dotenv import load_dotenv

# Load environment variables first!
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import PersistentAgentExecutor

def main():
    skill = AgentSkill(
        id="long_term_memory",
        name="Long Term Memory",
        description="Remember data persistently",
        tags=["memory", "persistence"],
        examples=["Remember that I like pizza"],
    )

    agent_card = AgentCard(
        name="memory_agent",
        description="Persistent Storage Agent for long-term memory",
        url="http://localhost:8031/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=PersistentAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting memory_agent on port 8031")
    port = int(os.getenv("PORT", 8031))
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
