"""User model for authentication and profile."""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Medical Profile ─────────────────────────────────
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)          # male / female / other
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    blood_type = Column(String(5), nullable=True)    # A+, O-, etc.
    medical_history = Column(Text, nullable=True)    # chronic conditions, past surgeries
    allergies = Column(Text, nullable=True)          # drug/food allergies
    current_medications = Column(Text, nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    symptoms = relationship("SymptomEntry", back_populates="user")

