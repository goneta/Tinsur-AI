
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import ToolAgentExecutor

def main():
    skill = AgentSkill(
        id="tool_search",
        name="Search",
        description="Search Google",
        tags=["search", "tool"],
        examples=["Search for cats"],
    )

    agent_card = AgentCard(
        name="Tool Agent",
        description="Agent with tools (Replication of 2-tool-agent)",
        url="http://localhost:8002/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ToolAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_tool_agent on port 8002")
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
