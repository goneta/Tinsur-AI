
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import MultiAgentExecutor

def main():
    skill = AgentSkill(
        id="manage_tasks",
        name="Manage Tasks",
        description="Delegate writing and reviewing",
        tags=["manager", "delegation"],
        examples=["Write a story"],
    )

    agent_card = AgentCard(
        name="Multi Agent Manager",
        description="Agent that delegates (Replication of 7-multi-agent)",
        url="http://localhost:8007/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=MultiAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_multi_agent on port 8007")
    uvicorn.run(server.build(), host="0.0.0.0", port=8007)

if __name__ == "__main__":
    main()
