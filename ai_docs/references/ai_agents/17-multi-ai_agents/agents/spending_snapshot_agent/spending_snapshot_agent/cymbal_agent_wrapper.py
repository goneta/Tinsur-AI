from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

bank_agent_wrapper = RemoteA2aAgent(
    name="cymbal_agent",
    description=(
        "A client for the Cymbal bank agent to request information about about user's bank and other financial information."
    ),
    agent_card="https://agent.ai-agent-bakeoff.com/.well-known/agent-card.json",
)
