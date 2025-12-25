import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import AdkLiveAgentExecutor
from dotenv import load_dotenv
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
load_dotenv(env_path, override=True)

def main():
    skill = AgentSkill(
        id="multimodal_live",
        name="Multimodal Live",
        description="Real-time multimodal interactions (Voice, Vision)",
        tags=["live", "multimodal", "voice", "vision"],
        examples=["Handle a voice request", "Analyze this stream"],
    )

    agent_card = AgentCard(
        name="ADK Live Agent",
        description="Real-time multimodal agent for Voice/Vision",
        url="http://localhost:8035/",
        defaultInputModes=["text", "audio", "video"],
        defaultOutputModes=["text", "audio"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=AdkLiveAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    port = 8035
    print(f"Starting adk_live on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
