from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import logging

from app.core.database import get_db, SessionLocal
from app.core.dependencies import get_current_user, require_agent
from app.models.user import User
from app.core.agent_client import AgentClient
from app.services.security_service import SecurityService
from app.services.ai_service import AiService
from app.models.client import Client
from app.models.chat import ChatChannel, ChatChannelMember, ChatMessage as ChatMessageModel
from app.schemas.chat import (
    ChatChannelCreate,
    ChatChannelResponse,
    ChatChannelMemberResponse,
    ChatMessageCreate,
    ChatMessageResponse,
)

_ws_logger = logging.getLogger("api.chat.ws")

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    policy_id: Optional[str] = None
    image_path: Optional[str] = None
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    
class ChatResponse(BaseModel):
    response: str

class ChatReactionRequest(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=10)
    action: str = Field(default="add", pattern="^(add|remove)$")

class ChatChannelInviteRequest(BaseModel):
    user_ids: List[UUID] = Field(default_factory=list, min_length=1)
    
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

    import logging
    logger = logging.getLogger("api.chat")

    # Sanitize image_path to prevent path traversal
    if request.image_path:
        import os
        normalized = os.path.normpath(request.image_path)
        if '..' in normalized or normalized.startswith('/etc') or normalized.startswith('/root'):
            raise HTTPException(status_code=400, detail="Invalid image path")

    # Find client_id if user is a client
    client_id = None
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if client:
            client_id = str(client.id)

    # --- Strategy 1: Direct in-process agent execution ---
    use_direct = True
    MultiAgentExecutor = None
    try:
        try:
            from backend.agents.a2a_multi_agent.agent_executor import MultiAgentExecutor
        except ImportError:
            from agents.a2a_multi_agent.agent_executor import MultiAgentExecutor
    except ImportError as e:
        logger.warning(f"Direct agent import unavailable, will use HTTP fallback: {e}")
        use_direct = False

    if use_direct and MultiAgentExecutor is not None:
        try:
            from a2a.server.agent_execution.context import RequestContext
            from a2a.server.events.event_queue import EventQueue
            from a2a.types import AgentMessage

            executor = MultiAgentExecutor()

            events = [AgentMessage(type="user_text_message", text=request.message)]
            if request.image_path:
                events.append(AgentMessage(type="user_image_message", path=request.image_path))

            req_context = RequestContext(
                events=events,
                metadata={
                    "user_id": str(current_user.id),
                    "client_id": client_id,
                    "company_id": str(current_user.company_id) if current_user.company_id else None,
                    "policy_id": request.policy_id,
                    "history": [h.dict() for h in request.history] if request.history else [],
                    "google_api_key": api_key,
                    **context
                }
            )

            queue = EventQueue()
            await executor.execute(req_context, queue)

            # Extract response from event queue
            response_text = "I'm sorry, I couldn't process your request."
            for event in reversed(queue.events):
                if isinstance(event, dict):
                    if event.get("type") == "agent_text_message":
                        response_text = event.get("text") or event.get("content") or response_text
                        break
                elif getattr(event, "type", "") == "agent_text_message":
                    if hasattr(event, "text"):
                        response_text = event.text
                    elif hasattr(event, "content"):
                        response_text = event.content
                    break

            if plan == "CREDIT":
                ai_service.log_and_consume_usage(
                    str(current_user.company_id),
                    str(current_user.id),
                    "orchestrator_agent"
                )

            return ChatResponse(response=response_text)

        except Exception as e:
            import traceback
            logger.error(f"Direct agent execution failed: {e}")
            logger.error(traceback.format_exc())
            # Fall through to HTTP fallback instead of crashing
            logger.info("Falling back to HTTP agent client...")

    # --- Strategy 2: HTTP Client fallback ---
    try:
        http_client = AgentClient()
        response = await http_client.send_message(
            agent_name="orchestrator_agent",
            message=request.message,
            context=context,
            api_key=api_key
        )

        if "error" not in response and plan == "CREDIT":
            ai_service.log_and_consume_usage(
                str(current_user.company_id),
                str(current_user.id),
                "orchestrator_agent"
            )

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        response_text = "I'm sorry, I couldn't understand that."
        if "messages" in response and isinstance(response["messages"], list):
            if len(response["messages"]) > 0:
                last_msg = response["messages"][-1]
                response_text = last_msg.get("text") or last_msg.get("content") or response_text

        return ChatResponse(response=response_text)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HTTP agent client also failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI service temporarily unavailable: {str(e)}")


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token for authentication"),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time streaming AI chat.

    Protocol
    --------
    Client sends JSON:  {"message": "...", "policy_id": "...", "history": [...]}
    Server sends JSON chunks:
      {"type": "token",   "text": "partial text"}
      {"type": "done",    "provider": "openai", "model": "gpt-4o-mini"}
      {"type": "error",   "detail": "reason"}
      {"type": "credits", "balance": 42.5}   (if on CREDIT plan)
    """
    await websocket.accept()

    # ── Authenticate via token query param ──────────────────────────────────
    current_user: Optional[User] = None
    try:
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("No sub in token")
        current_user = db.query(User).filter(User.id == user_id).first()
    except Exception as exc:
        _ws_logger.warning(f"WS auth failed: {exc}")
        await websocket.send_json({"type": "error", "detail": "Authentication failed"})
        await websocket.close(code=4001)
        return

    if not current_user or not current_user.is_active:
        await websocket.send_json({"type": "error", "detail": "User not found or inactive"})
        await websocket.close(code=4001)
        return

    ai_service = AiService(db)

    try:
        while True:
            # ── Receive message ────────────────────────────────────────────
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON"})
                continue

            message: str = data.get("message", "").strip()
            history: List[Dict[str, str]] = data.get("history", [])
            if not message:
                await websocket.send_json({"type": "error", "detail": "Empty message"})
                continue

            # ── Check AI access ────────────────────────────────────────────
            company_id = str(current_user.company_id) if current_user.company_id else None
            _api_key, plan, can_use = ai_service.get_effective_ai_config(company_id)
            if not can_use:
                code = "no_credits" if plan == "CREDIT" else "plan_restricted"
                await websocket.send_json({"type": "error", "detail": code})
                continue

            # ── Build LLM router & stream ──────────────────────────────────
            router = ai_service.get_llm_router(
                company_id=company_id,
                system_prompt=(
                    "You are an AI assistant for an insurance platform. "
                    "Answer concisely and professionally."
                ),
            )
            if router is None:
                await websocket.send_json({"type": "error", "detail": "AI not configured"})
                continue

            collected_text = ""
            try:
                async for chunk in router.stream(message, max_tokens=1024):
                    if chunk:
                        collected_text += chunk
                        await websocket.send_json({"type": "token", "text": chunk})
            except Exception as stream_err:
                _ws_logger.error(f"Streaming error: {stream_err}")
                # Fall back to non-streaming
                resp = await router.generate(message, history=history)
                collected_text = resp.text
                await websocket.send_json({"type": "token", "text": collected_text})

            await websocket.send_json({
                "type": "done",
                "provider": router.provider,
                "model": router.model,
            })

            # ── Consume credits ────────────────────────────────────────────
            if plan == "CREDIT" and current_user.company_id:
                ai_service.log_and_consume_usage(
                    str(current_user.company_id),
                    str(current_user.id),
                    "websocket_chat",
                )
                # Refresh company balance
                from app.models.company import Company
                company = db.query(Company).filter(Company.id == current_user.company_id).first()
                if company:
                    await websocket.send_json({"type": "credits", "balance": float(company.ai_credits_balance)})

    except WebSocketDisconnect:
        _ws_logger.info(f"WS disconnected: user={current_user.id if current_user else 'unknown'}")
    except Exception as exc:
        _ws_logger.error(f"WS error: {exc}")
        try:
            await websocket.send_json({"type": "error", "detail": str(exc)})
        except Exception:
            pass


@router.post("/channels", response_model=ChatChannelResponse)
def create_chat_channel(
    payload: ChatChannelCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Create a chat channel for internal staff."""
    payload.company_id = current_user.company_id
    payload.created_by = current_user.id

    channel = ChatChannel(
        company_id=payload.company_id,
        name=payload.name,
        is_private=payload.is_private,
        created_by=payload.created_by,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    if channel.is_private:
        member_ids = set(payload.member_ids or [])
        member_ids.add(current_user.id)
        _add_channel_members(db, channel.id, current_user, list(member_ids))
    return channel


@router.get("/channels", response_model=List[ChatChannelResponse])
def list_chat_channels(
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """List chat channels for the current company."""
    member_subquery = db.query(ChatChannelMember.channel_id).filter(
        ChatChannelMember.user_id == current_user.id
    ).subquery()
    return (
        db.query(ChatChannel)
        .filter(ChatChannel.company_id == current_user.company_id)
        .filter(or_(ChatChannel.is_private.is_(False), ChatChannel.id.in_(member_subquery)))
        .order_by(ChatChannel.created_at.desc())
        .all()
    )


@router.get("/channels/{channel_id}/members", response_model=List[ChatChannelMemberResponse])
def list_channel_members(
    channel_id: UUID,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """List members of a private channel."""
    channel = db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
    if not channel or channel.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Channel not found")

    _ensure_channel_access(db, channel, current_user)
    return db.query(ChatChannelMember).filter(ChatChannelMember.channel_id == channel_id).all()


@router.post("/channels/{channel_id}/members", response_model=List[ChatChannelMemberResponse])
def invite_channel_members(
    channel_id: UUID,
    payload: ChatChannelInviteRequest,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Invite members to a private channel."""
    channel = db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
    if not channel or channel.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Channel not found")

    _ensure_channel_access(db, channel, current_user)
    if not channel.is_private:
        raise HTTPException(status_code=400, detail="Public channels do not require invitations")

    added_members = _add_channel_members(db, channel_id, current_user, payload.user_ids)
    return added_members


@router.post("/messages", response_model=ChatMessageResponse)
def send_chat_message(
    payload: ChatMessageCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Send a chat message in a channel."""
    channel = db.query(ChatChannel).filter(ChatChannel.id == payload.channel_id).first()
    if not channel or channel.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Channel not found")
    _ensure_channel_access(db, channel, current_user)

    message = ChatMessageModel(
        company_id=current_user.company_id,
        channel_id=payload.channel_id,
        sender_id=current_user.id,
        message=payload.message,
        attachments=payload.attachments or [],
        read_by=[str(current_user.id)],
        reactions=[],
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/messages", response_model=List[ChatMessageResponse])
def list_chat_messages(
    channel_id: UUID,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """List messages in a channel."""
    channel = db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
    if not channel or channel.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Channel not found")
    _ensure_channel_access(db, channel, current_user)

    return db.query(ChatMessageModel).filter(
        ChatMessageModel.channel_id == channel_id
    ).order_by(ChatMessageModel.created_at.desc()).limit(200).all()


@router.post("/messages/{message_id}/read", response_model=ChatMessageResponse)
def mark_message_read(
    message_id: UUID,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Mark a message as read by the current user."""
    message = db.query(ChatMessageModel).filter(ChatMessageModel.id == message_id).first()
    if not message or message.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Message not found")
    _ensure_message_access(db, message, current_user)

    read_by = set(message.read_by or [])
    read_by.add(str(current_user.id))
    message.read_by = list(read_by)
    db.commit()
    db.refresh(message)
    return message


@router.post("/messages/{message_id}/react", response_model=ChatMessageResponse)
def react_to_message(
    message_id: UUID,
    payload: ChatReactionRequest,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Add or remove a reaction to a message."""
    message = db.query(ChatMessageModel).filter(ChatMessageModel.id == message_id).first()
    if not message or message.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Message not found")
    _ensure_message_access(db, message, current_user)

    reactions = list(message.reactions or [])
    entry = {"emoji": payload.emoji, "user_id": str(current_user.id)}

    if payload.action == "add":
        if entry not in reactions:
            reactions.append(entry)
    else:
        reactions = [r for r in reactions if not (r.get("emoji") == payload.emoji and r.get("user_id") == str(current_user.id))]

    message.reactions = reactions
    db.commit()
    db.refresh(message)
    return message


def _ensure_channel_access(db: Session, channel: ChatChannel, current_user: User) -> None:
    if not channel.is_private:
        return
    membership = db.query(ChatChannelMember).filter(
        ChatChannelMember.channel_id == channel.id,
        ChatChannelMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You do not have access to this channel")


def _ensure_message_access(db: Session, message: ChatMessageModel, current_user: User) -> None:
    channel = db.query(ChatChannel).filter(ChatChannel.id == message.channel_id).first()
    if channel:
        _ensure_channel_access(db, channel, current_user)


def _add_channel_members(
    db: Session,
    channel_id: UUID,
    current_user: User,
    user_ids: List[UUID],
) -> List[ChatChannelMember]:
    if not user_ids:
        return []

    eligible_users = db.query(User).filter(
        User.id.in_(user_ids),
        User.company_id == current_user.company_id,
        User.user_type.in_(["company_admin", "manager", "agent", "receptionist", "admin", "super_admin"]),
    ).all()
    eligible_ids = {user.id for user in eligible_users}
    invalid_ids = [uid for uid in user_ids if uid not in eligible_ids]
    if invalid_ids:
        raise HTTPException(status_code=400, detail="One or more users are not eligible for this channel")

    existing_members = db.query(ChatChannelMember).filter(
        ChatChannelMember.channel_id == channel_id,
        ChatChannelMember.user_id.in_(user_ids),
    ).all()
    existing_ids = {member.user_id for member in existing_members}

    new_members = []
    for user_id in user_ids:
        if user_id in existing_ids:
            continue
        member = ChatChannelMember(
            channel_id=channel_id,
            user_id=user_id,
            added_by=current_user.id,
        )
        db.add(member)
        new_members.append(member)

    db.commit()
    for member in new_members:
        db.refresh(member)

    return existing_members + new_members
