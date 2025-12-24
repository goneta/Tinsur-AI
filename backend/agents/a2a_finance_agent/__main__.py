
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import FinanceAgentExecutor

def main():
    skill = AgentSkill(
        id="generate_report",
        name="Generate Report",
        description="Create financial report",
        tags=["finance", "report"],
        examples=["Generate Q4 report"],
    )

    agent_card = AgentCard(
        name="Finance Agent",
        description="Business Agent for Finance",
        url="http://localhost:8022/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=FinanceAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_finance_agent on port 8022")
    port = int(os.getenv("PORT", 8022))
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
