
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import CallbacksAgentExecutor

def main():
    skill = AgentSkill(
        id="run_callback",
        name="Callbacks",
        description="Run with callbacks",
        tags=["callbacks"],
        examples=["Hello"],
    )

    agent_card = AgentCard(
        name="Callbacks Agent",
        description="Agent with before/after callbacks (Replication of 9-callbacks)",
        url="http://localhost:8009/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=CallbacksAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_callbacks_agent on port 8009")
    uvicorn.run(server.build(), host="0.0.0.0", port=8009)

if __name__ == "__main__":
    main()
