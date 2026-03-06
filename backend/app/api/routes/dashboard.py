"""Dashboard routes — conversation stats and urgency trends."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.symptom import SymptomEntry
from app.api.middleware.auth import require_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get dashboard summary statistics for the user."""
    total_conversations = (
        db.query(func.count(Conversation.id))
        .filter(Conversation.user_id == user.id)
        .scalar()
    )

    total_symptoms = (
        db.query(func.count(SymptomEntry.id))
        .filter(SymptomEntry.user_id == user.id)
        .scalar()
    )

    # Urgency distribution
    urgency_dist = (
        db.query(Conversation.urgency_level, func.count(Conversation.id))
        .filter(
            Conversation.user_id == user.id,
            Conversation.urgency_level.isnot(None),
        )
        .group_by(Conversation.urgency_level)
        .all()
    )

    # Recent conversations
    recent = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_conversations": total_conversations,
        "total_symptom_entries": total_symptoms,
        "urgency_distribution": {
            str(level): count for level, count in urgency_dist
        },
        "recent_conversations": [
            {
                "id": c.id,
                "title": c.title,
                "urgency_level": c.urgency_level,
                "updated_at": c.updated_at,
            }
            for c in recent
        ],
    }
