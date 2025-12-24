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
