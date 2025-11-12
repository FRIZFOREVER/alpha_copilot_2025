import pytest

from ml.configs.model_config import (
    ModelSettings,
    get_keep_alive_from_env,
    get_model_from_env,
    list_configured_models,
)


def test_base_url_strips_whitespace() -> None:
    settings = ModelSettings.model_validate(
        {
            "base_url": " http://host ",
            "api_mode": "chat",
            "model": "dummy",
        }
    )

    assert settings.base_url == "http://host"


def test_model_resolves_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_REASONING_MODEL", "chat-model")
    settings = ModelSettings.model_validate({"api_mode": "chat"})

    assert settings.model == "chat-model"


def test_model_resolution_trims_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "  embed-model  ")

    resolved = get_model_from_env("embeddings")

    assert resolved == "embed-model"


def test_keep_alive_defaults_per_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_REASONING_MODEL", "chat-model")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "embed-model")
    monkeypatch.setenv("OLLAMA_RERANK_MODEL", "rerank-model")

    chat_settings = ModelSettings.model_validate({"api_mode": "chat"})
    embedding_settings = ModelSettings.model_validate({"api_mode": "embeddings"})
    rerank_settings = ModelSettings.model_validate({"api_mode": "reranker"})

    assert chat_settings.keep_alive == "30m"
    assert embedding_settings.keep_alive == "10m"
    assert rerank_settings.keep_alive == "10m"


def test_keep_alive_override_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_REASONING_MODEL", "chat-model")
    monkeypatch.setenv("OLLAMA_REASONING_KEEP_ALIVE", "  3600 ")

    settings = ModelSettings.model_validate({"api_mode": "chat"})

    assert settings.keep_alive == 3600


def test_missing_environment_variable_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OLLAMA_RERANK_MODEL", raising=False)

    with pytest.raises(ValueError):
        ModelSettings.model_validate({"api_mode": "reranker"})


def test_list_configured_models_filters_blank_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_REASONING_MODEL", "chat-model")
    monkeypatch.setenv("OLLAMA_RERANK_MODEL", "")
    monkeypatch.delenv("OLLAMA_EMBEDDING_MODEL", raising=False)

    configured = list_configured_models()

    assert configured == {"chat": "chat-model"}


def test_get_keep_alive_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_EMBEDDING_KEEP_ALIVE", "15m")

    keep_alive = get_keep_alive_from_env("embeddings")

    assert keep_alive == "15m"
