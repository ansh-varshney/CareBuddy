"""Symptom journal entry model for tracking symptoms over time."""

from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.models.database import Base


class SymptomEntry(Base):
    __tablename__ = "symptom_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    symptoms = Column(JSON, nullable=False)  # List of symptom strings
    description = Column(Text, nullable=True)  # Free text description
    severity = Column(Integer, nullable=True)  # 1-10 self-reported
    urgency_assessed = Column(Integer, nullable=True)  # 1-5 AI-assessed
    body_area = Column(String, nullable=True)  # e.g., "head", "chest", "abdomen"
    recommendation = Column(Text, nullable=True)  # AI recommendation summary
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="symptoms")
