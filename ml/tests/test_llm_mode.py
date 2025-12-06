import sys
from types import ModuleType

import pytest


_httpx_stub = ModuleType("httpx")
setattr(_httpx_stub, "Client", object)
setattr(_httpx_stub, "RequestError", Exception)
sys.modules.setdefault("httpx", _httpx_stub)

_pydantic_stub = ModuleType("pydantic")


class _BaseModel:
    pass


class _ConfigDict(dict):
    pass


def _field(*args, **kwargs):
    return None


def _field_validator(*args, **kwargs):  # type: ignore[no-untyped-def]
    def decorator(func):  # type: ignore[no-untyped-def]
        return func

    return decorator


setattr(_pydantic_stub, "BaseModel", _BaseModel)
setattr(_pydantic_stub, "ConfigDict", _ConfigDict)
setattr(_pydantic_stub, "Field", _field)
setattr(_pydantic_stub, "field_validator", _field_validator)
sys.modules.setdefault("pydantic", _pydantic_stub)

from ml.configs.llm_mode import (  # noqa: E402
    LLMMode,
    _resolve_provider_env_name,
    get_llm_mode,
    get_provider_api_key,
    get_provider_base_url,
)


@pytest.mark.parametrize(
    "mode, value",
    [
        (LLMMode.OLLAMA, "ollama"),
        (LLMMode.HUGGINGFACE, "huggingface"),
        (LLMMode.OPENROUTER, "openrouter"),
    ],
)
def test_llm_mode_enum_values(mode: LLMMode, value: str) -> None:
    assert mode.value == value


def test_get_llm_mode_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_MODE", raising=False)

    with pytest.raises(RuntimeError, match="Environment variable LLM_MODE is required"):
        get_llm_mode()


@pytest.mark.parametrize("value", ["ollama", "huggingface", "openrouter"])
def test_get_llm_mode_valid_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("LLM_MODE", value)

    assert get_llm_mode() is LLMMode(value)


@pytest.mark.parametrize("value", ["invalid", "123", "", "Ollama"])
def test_get_llm_mode_rejects_invalid(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("LLM_MODE", value)

    with pytest.raises(ValueError, match="LLM_MODE must be one of:"):
        get_llm_mode()


def test_get_provider_base_url_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HUGGINGFACE_BASE_URL", "https://example.com")

    assert get_provider_base_url(LLMMode.HUGGINGFACE) == "https://example.com"


@pytest.mark.parametrize(
    "env_name, mode",
    [
        ("HUGGINGFACE_BASE_URL", LLMMode.HUGGINGFACE),
        ("OPENROUTER_BASE_URL", LLMMode.OPENROUTER),
    ],
)
def test_get_provider_base_url_missing(monkeypatch: pytest.MonkeyPatch, env_name: str, mode: LLMMode) -> None:
    monkeypatch.delenv(env_name, raising=False)

    with pytest.raises(RuntimeError, match=f"Environment variable {env_name} is required"):
        get_provider_base_url(mode)


def test_get_provider_base_url_requires_mapping() -> None:
    with pytest.raises(ValueError, match="No environment mapping defined for LLM mode ollama"):
        get_provider_base_url(LLMMode.OLLAMA)


@pytest.mark.parametrize(
    "env_name, mode",
    [
        ("HUGGINGFACE_API_KEY", LLMMode.HUGGINGFACE),
        ("OPENROUTER_API_KEY", LLMMode.OPENROUTER),
    ],
)
def test_get_provider_api_key(monkeypatch: pytest.MonkeyPatch, env_name: str, mode: LLMMode) -> None:
    monkeypatch.setenv(env_name, "token")

    assert get_provider_api_key(mode) == "token"


@pytest.mark.parametrize(
    "env_name, mode",
    [
        ("HUGGINGFACE_API_KEY", LLMMode.HUGGINGFACE),
        ("OPENROUTER_API_KEY", LLMMode.OPENROUTER),
    ],
)
def test_get_provider_api_key_missing(monkeypatch: pytest.MonkeyPatch, env_name: str, mode: LLMMode) -> None:
    monkeypatch.delenv(env_name, raising=False)

    with pytest.raises(RuntimeError, match=f"Environment variable {env_name} is required"):
        get_provider_api_key(mode)


def test_resolve_provider_env_name_returns_expected_key() -> None:
    assert _resolve_provider_env_name(LLMMode.OPENROUTER, "api_key") == "OPENROUTER_API_KEY"


def test_resolve_provider_env_name_invalid_key() -> None:
    with pytest.raises(
        ValueError, match="Missing environment key mapping for missing_key in LLM mode huggingface"
    ):
        _resolve_provider_env_name(LLMMode.HUGGINGFACE, "missing_key")
