
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import ParallelAgentExecutor

def main():
    skill = AgentSkill(
        id="monitor_systems",
        name="Monitor Systems",
        description="Check systems concurrently",
        tags=["monitor", "parallel"],
        examples=["Check system status"],
    )

    agent_card = AgentCard(
        name="Parallel Agent",
        description="Agent with parallel capabilities (Replication of 11-parallel-agent)",
        url="http://localhost:8011/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ParallelAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_parallel_agent on port 8011")
    uvicorn.run(server.build(), host="0.0.0.0", port=8011)

if __name__ == "__main__":
    main()
