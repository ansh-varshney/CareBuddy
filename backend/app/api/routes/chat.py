"""Chat routes — REST and WebSocket endpoints for health conversations."""

import uuid
import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.api.middleware.auth import get_current_user, require_user
from app.core.llm_engine import chat, chat_stream, generate_title, get_active_model
from app.core.triage import assess_triage
from app.core.memory import memory
from app.core.safety import check_safety
from app.utils.validators import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a chat message and receive an AI response (non-streaming).

    If no conversation_id is provided, a new conversation is created.
    """
    conversation_id = data.conversation_id or str(uuid.uuid4())
    model = data.model or get_active_model()

    # Create conversation record if new
    if not data.conversation_id and user:
        title = await generate_title(data.message, model=model)
        conv = Conversation(
            id=conversation_id,
            user_id=user.id,
            title=title,
            model_used=model,
        )
        db.add(conv)
        db.commit()

    # Get AI response
    response_text = await chat(
        user_message=data.message,
        conversation_id=conversation_id,
        model=model,
    )

    # Check urgency from safety module
    _, _, urgency = check_safety(data.message)

    # Save messages to database if user is authenticated
    if user:
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=data.message,
        )
        ai_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            metadata_={"urgency_level": urgency} if urgency > 0 else None,
        )
        db.add(user_msg)
        db.add(ai_msg)

        # Update conversation urgency if higher than current
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv and (not conv.urgency_level or urgency > conv.urgency_level):
            conv.urgency_level = urgency

        db.commit()

    return ChatResponse(
        response=response_text,
        conversation_id=conversation_id,
        model_used=model,
        urgency_level=urgency if urgency > 0 else None,
    )


@router.websocket("/ws/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for streaming chat responses.
    Persists messages and conversations to the database.
    """
    await websocket.accept()

    # Authenticate user from token
    user: Optional[User] = None
    if token:
        from app.api.middleware.auth import get_current_user_from_token
        user = get_current_user_from_token(token, db)

    # Track if this is the first message (for title generation)
    is_first_message = True
    existing_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if existing_conv:
        is_first_message = False

    logger.info(f"WebSocket connected: {conversation_id}, user: {user.username if user else 'anonymous'}")

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_message = data.get("message", "")
            model = data.get("model", get_active_model())

            if not user_message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            # Build user health context for personalized responses
            user_context = None
            if user:
                user_context = _build_user_health_context(user)

            # Create conversation record on first message (with placeholder title)
            if is_first_message and user:
                placeholder_title = user_message[:50] + ("…" if len(user_message) > 50 else "")
                conv = Conversation(
                    id=conversation_id,
                    user_id=user.id,
                    title=placeholder_title,
                    model_used=model,
                )
                db.add(conv)
                db.commit()
                is_first_message = False

                # Generate real title in background — don't block streaming
                import asyncio
                asyncio.create_task(
                    _update_title_async(conversation_id, user_message, model, websocket)
                )

            # Stream response immediately
            full_response = ""
            async for chunk in chat_stream(
                user_message=user_message,
                conversation_id=conversation_id,
                model=model,
                user_context=user_context,
            ):
                full_response += chunk
                await websocket.send_json({"type": "chunk", "content": chunk})

            # Save messages to DB
            if user:
                _, _, urgency = check_safety(user_message)
                user_msg = Message(conversation_id=conversation_id, role="user", content=user_message)
                ai_msg = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=full_response,
                    metadata_={"urgency_level": urgency} if urgency > 0 else None,
                )
                db.add(user_msg)
                db.add(ai_msg)
                conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                if conv and (not conv.urgency_level or urgency > conv.urgency_level):
                    conv.urgency_level = urgency
                db.commit()

            await websocket.send_json({"type": "done"})


    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass


def _build_user_health_context(user: User) -> str:
    """Build a health context string from the user's medical profile."""
    parts = []
    if user.full_name:
        parts.append(f"Patient name: {user.full_name}")
    if user.age:
        parts.append(f"Age: {user.age}")
    if user.sex:
        parts.append(f"Sex: {user.sex}")
    if user.weight_kg:
        parts.append(f"Weight: {user.weight_kg} kg")
    if user.height_cm:
        parts.append(f"Height: {user.height_cm} cm")
    if user.blood_type:
        parts.append(f"Blood type: {user.blood_type}")
    if user.medical_history:
        parts.append(f"Medical history: {user.medical_history}")
    if user.allergies:
        parts.append(f"Known allergies: {user.allergies}")
    if user.current_medications:
        parts.append(f"Current medications: {user.current_medications}")
    return "\n".join(parts) if parts else ""


async def _update_title_async(
    conversation_id: str,
    user_message: str,
    model: str,
    websocket: WebSocket,
) -> None:
    """Background task: generate a real title and update the DB + notify frontend."""
    from app.models.database import SessionLocal
    try:
        title = await generate_title(user_message, model=model)
        # Update DB with real title
        async_db = SessionLocal()
        try:
            conv = async_db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conv:
                conv.title = title
                async_db.commit()
        finally:
            async_db.close()
        # Notify frontend to update sidebar title
        try:
            await websocket.send_json({"type": "title", "content": title})
        except Exception:
            pass  # WS may have closed already
    except Exception as e:
        logger.warning(f"Background title generation failed: {e}")


@router.get("/conversations")
async def list_conversations(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """List all conversations for the authenticated user."""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "model_used": c.model_used,
            "urgency_level": c.urgency_level,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "message_count": len(c.messages),
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get a conversation with all its messages."""
    conv = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
        .first()
    )
    if not conv:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": conv.id,
        "title": conv.title,
        "model_used": conv.model_used,
        "urgency_level": conv.urgency_level,
        "created_at": conv.created_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "metadata": m.metadata_,
                "created_at": m.created_at,
            }
            for m in sorted(conv.messages, key=lambda m: m.created_at)
        ],
    }


@router.post("/conversations/{conversation_id}/triage")
async def run_triage(
    conversation_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Run triage assessment on a conversation."""
    conversation_text = await memory.get_messages_as_text(conversation_id)
    if not conversation_text:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No conversation history found")

    result = await assess_triage(conversation_text)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Triage assessment failed")

    # Update conversation urgency
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        conv.urgency_level = result.urgency_level
        db.commit()

    return result.to_dict()
