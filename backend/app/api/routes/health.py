"""Health check endpoint."""

from fastapi import APIRouter
import httpx

from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    # Check Ollama connectivity
    ollama_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_status = "connected"
                models = [m["name"] for m in resp.json().get("models", [])]
            else:
                ollama_status = "error"
                models = []
    except Exception:
        ollama_status = "disconnected"
        models = []

    return {
        "status": "ok",
        "service": "CareBuddy API",
        "version": settings.APP_VERSION,
        "ollama": {
            "status": ollama_status,
            "base_url": settings.OLLAMA_BASE_URL,
            "available_models": models,
        },
    }
