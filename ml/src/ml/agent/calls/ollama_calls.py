import os

from openai import OpenAI
from ml.utils.formats import _rstrip_slash

_OLLAMA_BASE_URL = "http://ollama:11434/v1/"


def _get_env_var(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Environment variable {key} must be set for Ollama calls.")
    return value


class _OllamaClient:
    def __init__(self, 
                 *,
                 env_key: str) -> None:
        self.model_name = _get_env_var(env_key)
        self.client = OpenAI(base_url=_OLLAMA_BASE_URL, api_key="ollama")


class reasoning_model_client(_OllamaClient):
    def __init__(self):
        super().__init__("OLLAMA_REASONING_MODEL")


class rerank_model_client(_OllamaClient):
    def __init__(self):
        super().__init__("OLLAMA_RERANK_MODEL")


class embedding_model_client(_OllamaClient):
    def __init__(self):
        super().__init__("OLLAMA_EMBEDDING_MODEL")
