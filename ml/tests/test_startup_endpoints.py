from __future__ import annotations

import asyncio
import importlib
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

import tests.test_api_app as api_app_test_utils
from ml.configs import LLMMode


@pytest.fixture()
def startup_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    async def _return_empty_list() -> list[str]:
        return []

    async def _noop_download(available_models: list[str], requested_models: list[str]) -> None:
        return None

    async def _noop_async() -> None:
        return None

    async def _init_graph_log_client() -> api_app_test_utils.GraphLogWebSocketClient:
        return api_app_test_utils.DummyGraphLogWebSocketClient()

    monkeypatch.setattr(api_app_test_utils.app_module, "get_llm_mode", lambda: LLMMode.OLLAMA)
    monkeypatch.setattr(api_app_test_utils.app_module, "fetch_available_models", _return_empty_list)
    monkeypatch.setattr(api_app_test_utils.app_module, "get_models_from_env", _return_empty_list)
    monkeypatch.setattr(api_app_test_utils.app_module, "download_missing_models", _noop_download)
    monkeypatch.setattr(api_app_test_utils.app_module, "init_warmup_clients", _noop_async)
    monkeypatch.setattr(api_app_test_utils.app_module, "clients_warmup", _noop_async)
    monkeypatch.setattr(api_app_test_utils.app_module, "init_graph_log_client", _init_graph_log_client)

    app = api_app_test_utils.create_app()
    app.state.model_ready = asyncio.Event()
    app.state.model_ready.set()

    with TestClient(app) as test_client:
        yield test_client


def test_app_module_imports() -> None:
    module = importlib.import_module("ml.api.app")

    assert hasattr(module, "app")


def test_root_endpoint_responds(startup_client: TestClient) -> None:
    response = startup_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_responds(startup_client: TestClient) -> None:
    response = startup_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
