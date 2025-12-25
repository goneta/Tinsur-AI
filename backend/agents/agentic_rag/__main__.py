import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import AgenticRagAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)

def main():
    skill = AgentSkill(
        id="agentic_rag",
        name="Agentic RAG",
        description="Retrieval-Augmented Generation over internal data",
        tags=["rag", "retrieval", "knowledge"],
        examples=["Find details about policy X", "What are the rules for claims?"],
    )

    agent_card = AgentCard(
        name="Agentic RAG",
        description="ADK-based RAG agent for knowledge grounding",
        url="http://localhost:8036/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=AgenticRagAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    port = 8036
    print(f"Starting agentic_rag on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
