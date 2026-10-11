from fastapi import APIRouter
from config.settings import get_config_status

router = APIRouter(tags=["System"])


@router.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Universal Synthetic Users Research Platform",
        "llm_config": get_config_status()
    }


@router.get("/api/llm-config")
def get_llm_config():
    """Returns the current LLM configuration and whether OpenRouter is ready."""
    return get_config_status()
