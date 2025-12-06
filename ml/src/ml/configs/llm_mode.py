from __future__ import annotations

import os
from enum import Enum


class LLMMode(str, Enum):
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"


class _ProviderEnvKeys:
    API_KEY = "api_key"
    BASE_URL = "base_url"


_PROVIDER_ENV: dict[LLMMode, dict[str, str]] = {
    LLMMode.HUGGINGFACE: {
        _ProviderEnvKeys.API_KEY: "HUGGINGFACE_API_KEY",
        _ProviderEnvKeys.BASE_URL: "HUGGINGFACE_BASE_URL",
    },
    LLMMode.OPENROUTER: {
        _ProviderEnvKeys.API_KEY: "OPENROUTER_API_KEY",
        _ProviderEnvKeys.BASE_URL: "OPENROUTER_BASE_URL",
    },
}


def get_llm_mode() -> LLMMode:
    value = os.getenv("LLM_MODE")

    if value is None:
        raise RuntimeError("Environment variable LLM_MODE is required")

    try:
        return LLMMode(value)
    except ValueError as exc:
        raise ValueError(
            "LLM_MODE must be one of: 'ollama', 'huggingface', or 'openrouter'"
        ) from exc


def get_provider_base_url(mode: LLMMode) -> str:
    env_name = _resolve_provider_env_name(mode, _ProviderEnvKeys.BASE_URL)
    value = os.getenv(env_name)

    if value is None:
        raise RuntimeError(f"Environment variable {env_name} is required for LLM mode {mode.value}")

    return value


def get_provider_api_key(mode: LLMMode) -> str:
    env_name = _resolve_provider_env_name(mode, _ProviderEnvKeys.API_KEY)
    value = os.getenv(env_name)

    if value is None:
        raise RuntimeError(f"Environment variable {env_name} is required for LLM mode {mode.value}")

    return value


def _resolve_provider_env_name(mode: LLMMode, key: str) -> str:
    provider_env = _PROVIDER_ENV.get(mode)

    if provider_env is None:
        raise ValueError(f"No environment mapping defined for LLM mode {mode.value}")

    env_name = provider_env.get(key)

    if env_name is None:
        raise ValueError(f"Missing environment key mapping for {key} in LLM mode {mode.value}")

    return env_name
