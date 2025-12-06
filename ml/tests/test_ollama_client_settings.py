import httpx
import pytest

from ml.configs import ollama_client_settings as settings_module
from ml.configs.ollama_client_settings import ClientSettings, ReasoningClientSettings


class DummyResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def patch_httpx_client(monkeypatch: pytest.MonkeyPatch, responses: list[object]) -> None:
    responses_iter = iter(responses)

    def client_factory(*args, **kwargs):  # type: ignore[no-untyped-def]
        response_or_exc = next(responses_iter)

        class DummyClient:
            def __enter__(self):  # type: ignore[no-untyped-def]
                return self

            def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
                return False

            def get(self, url):  # type: ignore[no-untyped-def]
                if isinstance(response_or_exc, Exception):
                    raise response_or_exc
                return response_or_exc

        return DummyClient()

    monkeypatch.setattr(settings_module.httpx, "Client", client_factory)


def test_base_url_retains_provided_value() -> None:
    settings = ClientSettings(base_url="http://custom-url")

    assert settings.base_url == "http://custom-url"


def test_base_url_autodetection_uses_first_reachable(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_httpx_client(monkeypatch, [DummyResponse(200), DummyResponse(200)])

    settings = ClientSettings.model_validate({"base_url": None})

    assert settings.base_url == settings_module._DEFAULT_BASE_URLS[0]


def test_base_url_autodetection_raises_when_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_httpx_client(
        monkeypatch,
        [
            httpx.RequestError("unreachable", request=None),
            httpx.RequestError("unreachable", request=None),
        ],
    )

    with pytest.raises(ValueError):
        ClientSettings.model_validate({"base_url": None})


def test_reasoning_model_is_loaded_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_httpx_client(monkeypatch, [DummyResponse(200), DummyResponse(200)])
    monkeypatch.setenv("OLLAMA_REASONING_MODEL", "test-ollama-model")

    settings = ReasoningClientSettings.model_validate({"base_url": None, "model": None})

    assert settings.model == "test-ollama-model"


def test_reasoning_model_raises_without_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_httpx_client(monkeypatch, [DummyResponse(200), DummyResponse(200)])
    monkeypatch.delenv("OLLAMA_REASONING_MODEL", raising=False)

    with pytest.raises(RuntimeError) as excinfo:
        ReasoningClientSettings.model_validate({"base_url": None, "model": None})

    assert "Environment variable OLLAMA_REASONING_MODEL is required" in str(excinfo.value)
