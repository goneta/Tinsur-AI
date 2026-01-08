from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.agent_client import AgentClient
from app.services.security_service import SecurityService
from app.services.ai_service import AiService

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    message: str
    policy_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str
    
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the orchestrator agent with user context.
    """
    security = SecurityService(db)
    permissions = security.get_user_permissions(str(current_user.id))
    
    # Build context to pass to the agent
    context = {
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_role": current_user.role,
        "permissions": permissions,
        "company_id": str(current_user.company_id) if current_user.company_id else None,
        "policy_id": request.policy_id
    }
    
    ai_service = AiService(db)
    api_key, plan, can_use = ai_service.get_effective_ai_config(str(current_user.company_id))

    if not can_use:
        if plan == "BASIC":
            raise HTTPException(status_code=403, detail="AI features are not enabled for your current plan.")
        else:
            # Plan is CREDIT but balance is 0
            # Return 402 Payment Required for frontend to show modal
            raise HTTPException(status_code=402, detail="Insufficient AI credits. Please purchase more to continue.")

    # Direct execution of Orchestrator Agent (In-Process)
    # This avoids needing to run a separate process for the agent during development
    try:
        from backend.agents.a2a_multi_agent.agent_executor import MultiAgentExecutor
        from a2a.server.agent_execution.context import RequestContext
        from a2a.server.events.event_queue import EventQueue
        from a2a.types import AgentMessage
        
        # Initialize Executor
        executor = MultiAgentExecutor()
        
        # Prepare Context
        # We map the chat request into a user_text_message event
        events = []
        events.append(AgentMessage(
            type="user_text_message",
            text=request.message
        ))
        
        req_context = RequestContext(
            events=events,
            metadata={
                "user_id": str(current_user.id),
                "company_id": str(current_user.company_id) if current_user.company_id else None,
                "policy_id": request.policy_id,
                "google_api_key": api_key, # Pass the resolved key
                **context
            }
        )
        
        queue = EventQueue()
        
        # Execute Agent
        await executor.execute(req_context, queue)
        
        # Process Response from Queue
        # We look for the last 'agent_text_message'
        response_text = "I'm sorry, I couldn't process your request."
        
        # queue.events is a list of events added during execution
        # We iterate to find the answer
        for event in reversed(queue.events):
            # Handle Dict (from utils.py)
            if isinstance(event, dict):
                if event.get("type") == "agent_text_message":
                    response_text = event.get("text") or event.get("content") or response_text
                    break
            # Handle Object
            elif getattr(event, "type", "") == "agent_text_message":
                 # Check 'text' or 'content' attribute depending on Event object structure
                 # A2A Event usually has .text for text messages
                 if hasattr(event, "text"):
                     response_text = event.text
                 elif hasattr(event, "content"):
                     response_text = event.content
                 break
        
        # Optional: Log usage since we bypassed the client log logic
        if plan == "CREDIT":
             ai_service.log_and_consume_usage(
                str(current_user.company_id), 
                str(current_user.id), 
                "orchestrator_agent"
            )

        return ChatResponse(response=response_text)

    except ImportError as e:
        # Fallback to HTTP Client if import fails (unlikely given structure)
        print(f"Direct import failed, falling back to HTTP: {e}")
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Orchestrator Error: {str(e)}")

    # Fallback to original HTTP Client logic if direct execution skipped
    client = AgentClient()
    
    # Call the orchestrator agent with the resolved key
    response = await client.send_message(
        agent_name="orchestrator_agent", 
        message=request.message, 
        context=context,
        api_key=api_key
    )

    # If it was a success and plan is CREDIT, log usage
    if "error" not in response and plan == "CREDIT":
        ai_service.log_and_consume_usage(
            str(current_user.company_id), 
            str(current_user.id), 
            "orchestrator_agent"
        )
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
        
    # Extract text from agent response
    # Expecting standard normalized format if possible, but for now specific to A2A response
    response_text = "I'm sorry, I couldn't understand that."
    
    if "messages" in response and isinstance(response["messages"], list):
        if len(response["messages"]) > 0:
            last_msg = response["messages"][-1]
            if "text" in last_msg:
                response_text = last_msg["text"]
            elif "content" in last_msg:
                response_text = last_msg["content"]
                
    return ChatResponse(response=response_text)
