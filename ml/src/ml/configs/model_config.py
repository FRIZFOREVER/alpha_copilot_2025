import logging
from os import getenv
from typing import Any, Dict, Literal, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator

from ml.utils.formats import _rstrip_slash

_DEFAULT_BASE_URL = "http://ollama:11434/v1"
_VALID_BASE_URL_SCHEMES = {"http", "https"}

_MODEL_ENV_VARS = {
    "chat": "OLLAMA_REASONING_MODEL",
    "reranker": "OLLAMA_RERANK_MODEL",
    "embeddings": "OLLAMA_EMBEDDING_MODEL",
}

_KEEP_ALIVE_ENV_VARS = {
    "chat": "OLLAMA_REASONING_KEEP_ALIVE",
    "reranker": "OLLAMA_RERANK_KEEP_ALIVE",
    "embeddings": "OLLAMA_EMBEDDING_KEEP_ALIVE",
}

_DEFAULT_KEEP_ALIVE = {
    "chat": "30m",
    "reranker": "10m",
    "embeddings": "10m",
}



def _read_model_from_env(api_mode: Literal["chat", "embeddings", "reranker"]) -> Optional[str]:
    """Return the configured model name for the given mode, if present."""
    env_var = _MODEL_ENV_VARS[api_mode]
    value = getenv(env_var)
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


def get_model_from_env(api_mode: Literal["chat", "embeddings", "reranker"]) -> Optional[str]:
    """Public helper returning the model configured for a given api_mode."""
    return _read_model_from_env(api_mode)


def _coerce_keep_alive(value: str) -> Optional[Union[int, str]]:
    stripped = value.strip()
    if not stripped:
        return None

    try:
        return int(stripped)
    except ValueError:
        return stripped


def _read_keep_alive_from_env(
    api_mode: Literal["chat", "embeddings", "reranker"]
) -> Optional[Union[int, str]]:
    env_var = _KEEP_ALIVE_ENV_VARS[api_mode]
    value = getenv(env_var)
    if value is None:
        return None

    return _coerce_keep_alive(value)


def get_keep_alive_from_env(
    api_mode: Literal["chat", "embeddings", "reranker"]
) -> Optional[Union[int, str]]:
    """Public helper returning keep-alive override for a given api_mode."""

    return _read_keep_alive_from_env(api_mode)


def list_configured_models() -> Dict[Literal["chat", "embeddings", "reranker"], str]:
    """Return a mapping of api_mode to configured model names, excluding blanks."""
    configured: Dict[Literal["chat", "embeddings", "reranker"], str] = {}
    for mode in _MODEL_ENV_VARS:
        model_name = _read_model_from_env(mode)
        if model_name:
            configured[mode] = model_name
    return configured

DEFAULT_RERANK_JSON_SCHEMA = {
    "type": "object",
    "properties": {"label": {"type": "string", "enum": ["yes", "no"]}},
    "required": ["label"],
    "additionalProperties": False,
}


def _is_valid_base_url(candidate_url: str) -> bool:
    """Return True when candidate_url looks like an HTTP(S) endpoint."""
    if not candidate_url:
        return False

    parsed = urlparse(candidate_url)
    if parsed.scheme not in _VALID_BASE_URL_SCHEMES:
        return False

    if not parsed.netloc:
        return False

    return True


class ModelSettings(BaseModel):
    """
    Description:
        Runtime configuration for OpenAI-compatible clients, covering connection tuning, routing, and
        per-mode sampling controls shared between chat and embedding workloads.
        Non-chat modes always disable chat_json_mode to prevent incompatible payloads.

    Args:
        base_url (str, default="http://ollama:11434/v1"): Root endpoint for OpenAI-compatible traffic.
        api_key (Optional[str], default=None): Credential forwarded to the backend when required.
        timeout_s (float, default=60.0): Client-side request timeout in seconds.
        max_retries (int, default=3): Maximum retry attempts for transient request failures.
        api_mode (Literal["chat", "embeddings", "reranker"]): Selects backend route and default behaviours.
        model (Optional[str], default=None): Specific model identifier; falls back to env-derived value.
        temperature (float, default=0.2, bounds=[0.0, 2.0]): Sampling temperature; higher increases randomness.
        top_p (float, default=1.0, bounds=[0.0, 1.0]): Nucleus sampling cutoff expressed as probability mass.
        chat_json_mode (bool, default=False): Enables structured JSON output when supported by the backend.
        embed_batch_size (int, default=128): Maximum inputs joined into a single embedding request.
        keep_alive (Optional[Union[int, str]]): Duration Ollama keeps the model loaded between requests.

    Returns:
        ModelSettings: Configured model settings instance ready for downstream use.
    """
    # ---- Connection (applies to ALL calls)
    base_url: str = Field(_DEFAULT_BASE_URL, description="OpenAI-compatible root")
    api_key: Optional[str] = Field(None, description="Local servers often ignore; SDK requires something")

    timeout_s: float = Field(
        60.0,
        description="Max generation time in seconds before the client aborts",
    )

    max_retries: int = Field(
        3,
        description="Maximum retry attempts for transient request failures",
    )

    # ---- Routing / model id
    api_mode: Literal["chat", "embeddings", "reranker"] = Field(
        ...,
        description="Client mode to call; selects request shape and defaults",
    )

    model: Optional[str] = Field(
        default=None,
        description="Explicit model identifier; defaults to environment-based value for the selected api_mode",
    )

    # ---- Universal sampling defaults (used where applicable)
    temperature: float = Field(
        0.2,
        ge=0.0,
        le=2.0,
        description="Sampling temperature; higher is more random, must be between 0 and 2",
    )
    
    top_p: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling cutoff; probability mass threshold between 0 and 1",
    )

    # ---- CHAT ONLY (ignored by EmbeddingClient)
    chat_json_mode: bool = Field(
        default=False,
        description="Request structured JSON responses if the backend allows it",
    )

    rerank_json_schema: Dict[str, Any] = Field(
        default_factory=lambda: DEFAULT_RERANK_JSON_SCHEMA.copy(),
        description="JSON schema expected from rerank calls when none is explicitly provided.",
    )

    # ---- EMBEDDINGS ONLY (ignored by ChatClient)
    embed_batch_size: int = Field(
        default=128,
        description="Maximum inputs bundled into a single embedding request before chunking",
    )

    keep_alive: Optional[Union[int, str]] = Field(
        default=None,
        description=(
            "How long Ollama should keep this model loaded; defaults vary per api_mode but can be"
            " overridden via environment variables or explicit configuration."
        ),
    )

    @model_validator(mode="after")
    def ensure_base_url(self):
        candidate_url = (self.base_url or "").strip()

        if not _is_valid_base_url(candidate_url):
            logging.warning(
                "Invalid base_url '%s' provided; falling back to local endpoint '%s'.",
                candidate_url or "<empty>",
                _DEFAULT_BASE_URL,
            )
            self.base_url = _DEFAULT_BASE_URL
        else:
            self.base_url = _rstrip_slash(candidate_url)

        return self

    @model_validator(mode="after")
    def define_model(self):
        if self.model:
            return self

        model = get_model_from_env(self.api_mode)
        if not model:
            # Raise error in case it's not set in .env or it's unreachable
            env_var = _MODEL_ENV_VARS[self.api_mode]
            raise ValueError(f"""Can't automatically define model from api_mode:\n
                             Environment variable {env_var} not set for api_mode '{self.api_mode}'
                             """)

        self.model = model
        return self
    
    @model_validator(mode="after")
    def ensure_mode(self):
        if self.chat_json_mode and self.api_mode != "chat":
            json_mode = self.chat_json_mode
            api_mode = self.api_mode
            logging.warning(
                "Using chat_json_mode=%s while api_mode=%s", json_mode, api_mode
            )
            logging.warning(
                "Disabling chat_json_mode=%s for api_mode=%s", json_mode, api_mode
            )
            self.chat_json_mode = False
        return self

    @model_validator(mode="after")
    def ensure_keep_alive(self):
        if self.keep_alive is not None:
            return self

        env_keep_alive = _read_keep_alive_from_env(self.api_mode)
        if env_keep_alive is not None:
            self.keep_alive = env_keep_alive
        else:
            self.keep_alive = _DEFAULT_KEEP_ALIVE[self.api_mode]

        return self
