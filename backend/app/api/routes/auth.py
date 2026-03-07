"""Authentication routes — register, login, profile."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    require_user,
)
from app.utils.validators import UserRegister, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account with optional medical profile."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        # Medical profile
        age=data.age,
        sex=data.sex,
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        blood_type=data.blood_type,
        medical_history=data.medical_history,
        allergies=data.allergies,
        current_medications=data.current_medications,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token, username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate and receive a JWT token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token, username=user.username)


@router.get("/me")
async def get_profile(user: User = Depends(require_user)):
    """Get the currently authenticated user's full profile including medical info."""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "age": user.age,
        "sex": user.sex,
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "blood_type": user.blood_type,
        "medical_history": user.medical_history,
        "allergies": user.allergies,
        "current_medications": user.current_medications,
        "created_at": user.created_at,
    }


@router.put("/me")
async def update_profile(data: UserRegister, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Update the medical profile of the currently authenticated user."""
    for field in ["full_name", "age", "sex", "weight_kg", "height_cm",
                  "blood_type", "medical_history", "allergies", "current_medications"]:
        val = getattr(data, field, None)
        if val is not None:
            setattr(user, field, val)
    db.commit()
    return {"message": "Profile updated"}
