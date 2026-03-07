"""Symptom journal routes — CRUD for tracking symptoms over time."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.models.symptom import SymptomEntry
from app.api.middleware.auth import require_user
from app.core.triage import extract_symptoms
from app.utils.validators import SymptomEntryCreate

router = APIRouter(prefix="/api/symptoms", tags=["Symptom Journal"])


@router.post("/", status_code=201)
async def create_symptom_entry(
    data: SymptomEntryCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Log a new symptom journal entry."""
    entry = SymptomEntry(
        user_id=user.id,
        symptoms=data.symptoms,
        description=data.description,
        severity=data.severity,
        body_area=data.body_area,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "id": entry.id,
        "symptoms": entry.symptoms,
        "description": entry.description,
        "severity": entry.severity,
        "body_area": entry.body_area,
        "created_at": entry.created_at,
    }


@router.get("/")
async def list_symptom_entries(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """List symptom journal entries for the authenticated user."""
    entries = (
        db.query(SymptomEntry)
        .filter(SymptomEntry.user_id == user.id)
        .order_by(SymptomEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": e.id,
            "symptoms": e.symptoms,
            "description": e.description,
            "severity": e.severity,
            "urgency_assessed": e.urgency_assessed,
            "body_area": e.body_area,
            "recommendation": e.recommendation,
            "created_at": e.created_at,
        }
        for e in entries
    ]


@router.get("/{entry_id}")
async def get_symptom_entry(
    entry_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get a specific symptom journal entry."""
    entry = (
        db.query(SymptomEntry)
        .filter(SymptomEntry.id == entry_id, SymptomEntry.user_id == user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Symptom entry not found")

    return {
        "id": entry.id,
        "symptoms": entry.symptoms,
        "description": entry.description,
        "severity": entry.severity,
        "urgency_assessed": entry.urgency_assessed,
        "body_area": entry.body_area,
        "recommendation": entry.recommendation,
        "created_at": entry.created_at,
    }


@router.delete("/{entry_id}", status_code=204)
async def delete_symptom_entry(
    entry_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Delete a symptom journal entry."""
    entry = (
        db.query(SymptomEntry)
        .filter(SymptomEntry.id == entry_id, SymptomEntry.user_id == user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Symptom entry not found")

    db.delete(entry)
    db.commit()


@router.post("/extract")
async def extract_symptoms_from_text(
    body: dict,
    user: User = Depends(require_user),
):
    """Extract symptoms from free text using LLM."""
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    symptoms = await extract_symptoms(text)
    return {"symptoms": symptoms}
