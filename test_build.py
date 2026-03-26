import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'backend', 'agents', 'a2a_policy_agent'))

try:
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import InMemoryTaskStore
    from a2a.types import AgentCapabilities, AgentCard, AgentSkill
    from agent_executor import PolicyAgentExecutor

    skill = AgentSkill(id="test", name="test", description="test", tags=["test"], examples=["test"])
    agent_card = AgentCard(name="test", description="test", url="http://localhost:8021", skills=[skill], capabilities=AgentCapabilities())
    
    executor = PolicyAgentExecutor()
    handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
    
    print("Building server...")
    server = A2AStarletteApplication(http_handler=handler, agent_card=agent_card)
    app = server.build()
    print("Server build successful.")

except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
