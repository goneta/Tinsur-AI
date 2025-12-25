import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import ComplianceAmlAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)

def main():
    skill = AgentSkill(
        id="sanctions_screening",
        name="Sanctions Screening",
        description="Screen users against global sanctions lists and AML risk",
        tags=["compliance", "aml", "kyc", "sanctions"],
        examples=["Screen new registration: John Doe", "Assess AML risk for this user profile"],
    )

    agent_card = AgentCard(
        name="Compliance & AML Agent",
        description="Agent for regulatory compliance and risk assessment",
        url="http://localhost:8038/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ComplianceAmlAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    port = 8038
    print(f"Starting compliance_aml_agent on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
