"""Settings routes — model switching and configuration."""

import httpx
from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.core.llm_engine import get_active_model, set_active_model
from app.core.rag_pipeline import rag_retriever
from app.utils.validators import ModelSwitch

router = APIRouter(prefix="/api/settings", tags=["Settings"])
settings = get_settings()


@router.get("/models")
async def list_models():
    """List available Ollama models and the currently active one."""
    # Fetch actually installed models from Ollama
    installed = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                installed = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass

    return {
        "active_model": get_active_model(),
        "configured_models": settings.AVAILABLE_MODELS,
        "installed_models": installed,
    }


@router.put("/models")
async def switch_model(data: ModelSwitch):
    """Switch the active LLM model."""
    # Verify model is actually available in Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                installed = [m["name"] for m in resp.json().get("models", [])]
                # Check with and without tag (e.g., "llama3" matches "llama3:latest")
                found = any(
                    data.model_name == m or data.model_name == m.split(":")[0]
                    for m in installed
                )
                if not found:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Model '{data.model_name}' is not installed in Ollama. "
                        f"Run: ollama pull {data.model_name}",
                    )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Is it running?",
        )

    success = set_active_model(data.model_name)
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{data.model_name}' not in configured models: {settings.AVAILABLE_MODELS}",
        )

    return {
        "message": f"Switched to model: {data.model_name}",
        "active_model": get_active_model(),
    }


@router.get("/knowledge-base")
async def knowledge_base_stats():
    """Get knowledge base statistics."""
    return rag_retriever.get_stats()
