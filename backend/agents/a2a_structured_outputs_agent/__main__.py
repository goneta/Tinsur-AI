
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import StructuredAgentExecutor

def main():
    skill = AgentSkill(
        id="email_gen",
        name="Generate Email",
        description="Generate a structured email",
        tags=["email", "structured"],
        examples=["Write an email to my boss"],
    )

    agent_card = AgentCard(
        name="Structured Output Agent",
        description="Agent returning structured data (Replication of 4-structured-outputs)",
        url="http://localhost:8004/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=StructuredAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_structured_outputs_agent on port 8004")
    uvicorn.run(server.build(), host="0.0.0.0", port=8004)

if __name__ == "__main__":
    main()
