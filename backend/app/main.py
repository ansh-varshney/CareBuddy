"""
CareBuddy — AI-Powered Health Assistant
FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.database import init_db
from app.api.routes import health, auth, chat, symptoms, settings as settings_routes
from app.core.memory import memory
from app.core.rag_pipeline import rag_retriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
app_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────
    logger.info("🚀 Starting CareBuddy API...")
    logger.info(f"   Environment: {app_settings.APP_ENV}")
    logger.info(f"   Ollama URL:  {app_settings.OLLAMA_BASE_URL}")
    logger.info(f"   Default LLM: {app_settings.DEFAULT_MODEL}")

    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database init skipped (may not be available): {e}")

    # Pre-warm ChromaDB — loads embedding model into memory now, not on first request
    try:
        rag_retriever.warm_up()
    except Exception as e:
        logger.warning(f"⚠️  ChromaDB warm-up failed (non-fatal): {e}")

    yield

    # ── Shutdown ─────────────────────────────────────
    logger.info("👋 Shutting down CareBuddy API...")
    await memory.close()



# ── Create FastAPI App ───────────────────────────────────
app = FastAPI(
    title="CareBuddy API",
    description=(
        "AI-Powered Health Assistant — Intelligent conversational health guidance "
        "powered by Ollama LLMs with RAG-enhanced medical knowledge."
    ),
    version=app_settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────
cors_origins = [
    origin.strip()
    for origin in app_settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(symptoms.router)
app.include_router(settings_routes.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CareBuddy API",
        "version": app_settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
