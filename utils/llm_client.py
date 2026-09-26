import json
import re
import time
import warnings
from typing import List, Dict, Any, Optional
import requests

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

from config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_BASE_URL,
    OPENROUTER_APP_TITLE,
    OPENROUTER_HTTP_REFERER,
    is_openrouter_configured,
    get_openrouter_api_key,
    get_openrouter_model,
    get_openrouter_base_url
)

class OpenRouterError(Exception):
    """Base exception for OpenRouter LLM errors."""
    pass

class OpenRouterConfigurationError(OpenRouterError):
    """Raised when OPENROUTER_API_KEY or OPENROUTER_MODEL is not configured."""
    pass

class LLMClient:
    """Client for OpenRouter LLM completions with dynamic model selection and JSON handling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url

    @property
    def api_key(self) -> str:
        return self._api_key or get_openrouter_api_key()

    @property
    def model(self) -> str:
        return self._model or get_openrouter_model()

    @property
    def base_url(self) -> str:
        return (self._base_url or get_openrouter_base_url()).rstrip("/")

    def validate_configuration(self) -> None:
        """Ensures that both API key and Model are configured in environment / .env."""
        missing = []
        if not self.api_key:
            missing.append("OPENROUTER_API_KEY")
        if not self.model:
            missing.append("OPENROUTER_MODEL")
        if missing:
            raise OpenRouterConfigurationError(
                f"Missing required configuration in .env: {', '.join(missing)}. "
                f"Please update your .env file with valid values."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2000,
        retries: int = 3
    ) -> str:
        """
        Calls OpenRouter chat completions API using the configured model.
        """
        self.validate_configuration()

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": OPENROUTER_HTTP_REFERER,
            "X-Title": OPENROUTER_APP_TITLE,
            "Content-Type": "application/json"
        }

        # Guard against OpenRouter's meta-tag 'openrouter/free' which routes to nvidia/nemotron content-safety
        target_model = self.model
        if target_model.strip().lower() in ["openrouter/free", "'openrouter/free'", '"openrouter/free"']:
            import warnings as _w
            _w.warn(
                "OPENROUTER_MODEL is set to 'openrouter/free' which routes to a content-safety model. "
                "Auto-rerouting to 'nex-agi/nex-n2.5-mini:free'. Update OPENROUTER_MODEL in .env to suppress this warning.",
                UserWarning,
                stacklevel=2
            )
            target_model = "nex-agi/nex-n2.5-mini:free"

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        last_err = None
        for attempt in range(1, retries + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise OpenRouterError(f"No choices returned from OpenRouter: {data}")
                    content = choices[0].get("message", {}).get("content", "").strip()

                    # Detect if a safety classification model (e.g. Nemotron content-safety) was accidentally invoked
                    if content.startswith("User Safety:") or "Response Safety:" in content:
                        # Reroute to a confirmed conversational chat model
                        payload["model"] = "nex-agi/nex-n2.5-mini:free"
                        retry_resp = requests.post(url, headers=headers, json=payload, timeout=60)
                        if retry_resp.status_code == 200:
                            retry_data = retry_resp.json()
                            if retry_data.get("choices"):
                                content = retry_data["choices"][0].get("message", {}).get("content", "").strip()
                    return content
                elif response.status_code in (429, 500, 502, 503, 504):
                    # Rate limit or temporary gateway error, backoff and retry
                    last_err = f"HTTP {response.status_code}: {response.text}"
                    time.sleep(2 * attempt)
                    continue
                else:
                    raise OpenRouterError(f"OpenRouter API error (HTTP {response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                last_err = str(e)
                time.sleep(2 * attempt)

        raise OpenRouterError(f"Failed to communicate with OpenRouter after {retries} attempts. Error: {last_err}")

    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: Optional[int] = 3500,
        retries: int = 3
    ) -> Any:
        """
        Calls OpenRouter and extracts parsed JSON data from the model output.
        Handles markdown json fences (```json ... ```) and raw json outputs.
        """
        raw_text = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            retries=retries
        )

        # Attempt direct JSON parse
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass

        # Try extracting from code block
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
        if match:
            candidate = match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Try searching for outermost brackets [ ... ] or { ... }
        b_match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw_text)
        if b_match:
            candidate = b_match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise OpenRouterError(f"Model output could not be parsed as valid JSON. Raw output:\n{raw_text}")

# Global instance for shared use
llm_client = LLMClient()
