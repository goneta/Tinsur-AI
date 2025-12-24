
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import SessionAgentExecutor

def main():
    skill = AgentSkill(
        id="remember_name",
        name="Remember Name",
        description="Remember user name in session",
        tags=["memory", "session"],
        examples=["My name is John"],
    )

    agent_card = AgentCard(
        name="Session Agent",
        description="Agent with session state (Replication of 5-sessions-and-state)",
        url="http://localhost:8005/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=SessionAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_sessions_state_agent on port 8005")
    uvicorn.run(server.build(), host="0.0.0.0", port=8005)

if __name__ == "__main__":
    main()
