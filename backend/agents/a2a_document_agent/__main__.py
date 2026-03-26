
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import DocumentAgentExecutor
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))


def main():
    share_skill = AgentSkill(
        id="share_document",
        name="Share Document",
        description="Share a document with specific permissions (A/B/C)",
        tags=["document", "collaboration", "sharing"],
        examples=["Share Policy PDF with Company Y (B2B, Option 2, Type A)"],
    )
    
    revoke_skill = AgentSkill(
        id="revoke_document_access",
        name="Revoke Document Access",
        description="Revoke access to a shared document",
        tags=["document", "security"],
        examples=["Revoke access to document D"],
    )

    agent_card = AgentCard(
        name="Document Agent",
        description="Agent for Secure Document Sharing & Collaboration",
        url="http://localhost:8032/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[share_skill, revoke_skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=DocumentAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_document_agent on port 8032")
    uvicorn.run(server.build(), host="0.0.0.0", port=8032)

if __name__ == "__main__":
    main()
