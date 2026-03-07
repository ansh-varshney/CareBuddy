"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings with defaults for local development."""

    # ── App ─────────────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "CareBuddy"
    APP_VERSION: str = "1.0.0"

    # ── Ollama LLM ──────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "llama3"
    AVAILABLE_MODELS: List[str] = [
        "llama3",
        "mistral",
        "gemma",
        "qwen2",
        "medllama2",
    ]

    # ── Database ────────────────────────────────────────
    DATABASE_URL: str = (
        "sqlite:///./carebuddy.db"
    )

    # ── Auth ────────────────────────────────────────────
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # ── CORS ────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:4200"

    # ── ChromaDB ────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "medical_knowledge"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings singleton."""
    return Settings()
