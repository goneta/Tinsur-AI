
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import RagAgentExecutor

def main():
    skill = AgentSkill(
        id="retrieve_knowledge",
        name="Retrieve Knowledge",
        description="RAG capabilities",
        tags=["rag", "knowledge"],
        examples=["What does the doc say about X?"],
    )

    agent_card = AgentCard(
        name="RAG Agent",
        description="Agent with Retrieval Augmented Generation (Replication of 14-adk-rag-agent)",
        url="http://localhost:8014/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=RagAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_adk_rag_agent on port 8014")
    uvicorn.run(server.build(), host="0.0.0.0", port=8014)

if __name__ == "__main__":
    main()
