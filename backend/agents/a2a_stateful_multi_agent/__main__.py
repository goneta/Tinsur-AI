
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import StatefulMultiAgentExecutor

def main():
    skill = AgentSkill(
        id="handle_support",
        name="Support",
        description="Handle customer support with state",
        tags=["support", "stateful"],
        examples=["I need help with my connection"],
    )

    agent_card = AgentCard(
        name="Stateful Multi Agent",
        description="Agent with stateful transfers (Replication of 8-stateful-multi-agent)",
        url="http://localhost:8008/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=StatefulMultiAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_stateful_multi_agent on port 8008")
    uvicorn.run(server.build(), host="0.0.0.0", port=8008)

if __name__ == "__main__":
    main()
