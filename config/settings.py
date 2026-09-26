import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

# Ensure .env is loaded from workspace root
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=False)

def get_openrouter_api_key() -> str:
    # Refresh from .env if needed
    if not os.getenv("OPENROUTER_API_KEY") and env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    val = os.getenv("OPENROUTER_API_KEY", "").strip()
    return val.strip("'\"")

def get_openrouter_model() -> str:
    if not os.getenv("OPENROUTER_MODEL") and env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    val = os.getenv("OPENROUTER_MODEL", "").strip()
    return val.strip("'\"")

def get_openrouter_base_url() -> str:
    val = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
    return val.strip("'\"")

# OpenRouter LLM Configuration — strictly driven by environment variables
OPENROUTER_API_KEY = get_openrouter_api_key()
OPENROUTER_MODEL = get_openrouter_model()
OPENROUTER_BASE_URL = get_openrouter_base_url()
OPENROUTER_APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "Synthetic Users Research Platform").strip()
OPENROUTER_HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost:8000").strip()

# Platform configuration settings
DEFAULT_N = 5
SENTIMENT_POSITIVE_THRESHOLD = 0.60
SENTIMENT_NEGATIVE_THRESHOLD = 0.35
MEMORY_WINDOW = 12
DATA_DIR = "data"
REPORTS_DIR = "reports"

def is_openrouter_configured() -> bool:
    """Checks if both OPENROUTER_API_KEY and OPENROUTER_MODEL are present in environment."""
    return bool(get_openrouter_api_key() and get_openrouter_model())

def get_config_status() -> dict:
    """Returns the current LLM configuration status without exposing sensitive secrets."""
    model = get_openrouter_model()
    return {
        "configured": is_openrouter_configured(),
        "has_api_key": bool(get_openrouter_api_key()),
        "model": model if model else None,
        "base_url": get_openrouter_base_url()
    }
