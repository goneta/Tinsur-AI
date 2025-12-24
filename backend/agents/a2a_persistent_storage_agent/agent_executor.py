from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
import uuid
import logging
from app.core.database import SessionLocal
from app.models.agent_memory import AgentMemory

logger = logging.getLogger(__name__)

class PersistentAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = Agent(
            name="memory_agent",
            model="gemini-2.0-flash",
            description="Agent that remembers facts about users persistently in the database",
            instruction="""
            You are a long-term memory assistant for Insurance SaaS.
            You help store and retrieve information about users persistently.
            """
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = ""
        user_id = None
        metadata = context.metadata or {}
        
        # Extract user_id from metadata
        user_id_str = metadata.get("user_id")
        if user_id_str:
            try:
                user_id = uuid.UUID(user_id_str)
            except ValueError:
                pass

        if context.events:
             for event in reversed(context.events):
                 if event.type == "user_text_message":
                     user_input = event.text
                     break
        
        db = SessionLocal()
        try:
            # Protocol: "remember that [content]" or "save [key]: [content]"
            if "remember that" in user_input.lower():
                content = user_input.split("remember that")[-1].strip()
                # Default key if not specified
                key = "general_info"
                
                new_memory = AgentMemory(
                    user_id=user_id,
                    agent_id=metadata.get("calling_agent", "main_orchestrator"),
                    memory_key=key,
                    content=content,
                    metadata_json={"original_input": user_input}
                )
                db.add(new_memory)
                db.commit()
                response_text = f"✅ Context Saved: {content[:100]}..."
                
            elif "what do you remember" in user_input.lower() or "find memory" in user_input.lower():
                query = db.query(AgentMemory)
                if user_id:
                    query = query.filter(AgentMemory.user_id == user_id)
                
                memories = query.all()
                if memories:
                    mem_list = "\n".join([f"- **{m.memory_key}**: {m.content}" for m in memories])
                    response_text = f"🔍 **Long-term Memory Retrieval**:\n{mem_list}"
                else:
                    response_text = "I don't have any memories for this context yet."
            else:
                # Use LLM to respond or decide what to do
                response_text = await self.agent.run(user_input)
                
            event_queue.enqueue_event(new_agent_text_message(response_text))
        except Exception as e:
            db.rollback()
            logger.error(f"Persistence Error: {str(e)}")
            event_queue.enqueue_event(new_agent_text_message(f"⚠️ Persistence Error: {str(e)}"))
        finally:
            db.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
