
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import LoopAgentExecutor

def main():
    skill = AgentSkill(
        id="improve_post",
        name="Improve Post",
        description="Improve a post iteratively",
        tags=["loop", "iteration"],
        examples=["Improve this post"],
    )

    agent_card = AgentCard(
        name="Loop Agent",
        description="Agent requiring approval loop (Replication of 12-loop-agent)",
        url="http://localhost:8012/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=LoopAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_loop_agent on port 8012")
    uvicorn.run(server.build(), host="0.0.0.0", port=8012)

if __name__ == "__main__":
    main()
