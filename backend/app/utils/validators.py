"""Input validation helpers."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UserRegister(BaseModel):
    """Registration request schema — includes optional medical profile."""
    email: str = Field(..., min_length=5, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = None
    # Medical profile (all optional)
    age: Optional[int] = Field(None, ge=1, le=120)
    sex: Optional[str] = Field(None, pattern="^(male|female|other)$")
    weight_kg: Optional[float] = Field(None, ge=1, le=500)
    height_cm: Optional[float] = Field(None, ge=30, le=300)
    blood_type: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email address format")
        return v.lower()


class UserLogin(BaseModel):
    """Login request schema."""
    username: str
    password: str


class UserProfile(BaseModel):
    """User profile response schema."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_type: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat message request schema."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str
    conversation_id: str
    model_used: str
    urgency_level: Optional[int] = None


class SymptomEntryCreate(BaseModel):
    """Create symptom journal entry schema."""
    symptoms: list[str] = Field(..., min_length=1)
    description: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=10)
    body_area: Optional[str] = None


class ModelSwitch(BaseModel):
    """Model switching request schema."""
    model_name: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    username: str
