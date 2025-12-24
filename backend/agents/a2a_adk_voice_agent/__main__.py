
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import VoiceAgentExecutor

def main():
    skill = AgentSkill(
        id="voice_chat",
        name="Voice Chat",
        description="Speak with the agent",
        tags=["voice", "speech"],
        examples=["Talk to me"],
    )

    agent_card = AgentCard(
        name="Voice Agent",
        description="Agent requiring Voice (Replication of 15-adk-voice-agent)",
        url="http://localhost:8015/",
        defaultInputModes=["text"], # A2A currently text/custom, voice via client
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=VoiceAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("Starting a2a_adk_voice_agent on port 8015")
    uvicorn.run(server.build(), host="0.0.0.0", port=8015)

if __name__ == "__main__":
    main()
