import asyncio
import sys
from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from types import ModuleType
from typing import ContextManager, Literal

import pytest
from fastapi.testclient import TestClient


def _install_stub_module(module_name: str, **attributes) -> None:
    if module_name in sys.modules:
        return

    stub_module = ModuleType(module_name)
    for attribute_name, attribute_value in attributes.items():
        setattr(stub_module, attribute_name, attribute_value)

    sys.modules[module_name] = stub_module


_install_stub_module("openai", AsyncOpenAI=type("AsyncOpenAI", (), {}))
_install_stub_module(
    "ollama",
    AsyncClient=type("AsyncClient", (), {}),
    ListResponse=type("ListResponse", (), {"models": []}),
    ProgressResponse=type("ProgressResponse", (), {}),
    list=lambda: type("ListResponse", (), {"models": []})(),
    pull=lambda model, stream: iter(()),
)
_install_stub_module("minio", Minio=type("Minio", (), {}))
_install_stub_module("ddgs", DDGS=type("DDGS", (), {}))
_install_stub_module("bs4", BeautifulSoup=type("BeautifulSoup", (), {}))

ollama_types = ModuleType("ollama._types")


class _StubChatResponse:  # pragma: no cover - dummy data container
    def __init__(self, message: object | None = None) -> None:
        self.message = message

    def model_dump_json(self) -> str:
        return "{}"


setattr(ollama_types, "ChatResponse", _StubChatResponse)
sys.modules["ollama._types"] = ollama_types

websockets_asyncio_client = ModuleType("websockets.asyncio.client")
websockets_asyncio_connection = ModuleType("websockets.asyncio.connection")


class _WebsocketState:
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class _DummyClientConnection:
    state = _WebsocketState.CLOSED

    async def wait_closed(self) -> None:  # pragma: no cover - dummy
        return None

    async def close(self) -> None:  # pragma: no cover - dummy
        return None


async def _connect(url: str, additional_headers: dict[str, str] | None = None) -> _DummyClientConnection:
    return _DummyClientConnection()


setattr(websockets_asyncio_client, "ClientConnection", _DummyClientConnection)
setattr(websockets_asyncio_client, "connect", _connect)
setattr(websockets_asyncio_connection, "State", _WebsocketState)

sys.modules["websockets.asyncio.client"] = websockets_asyncio_client
sys.modules["websockets.asyncio.connection"] = websockets_asyncio_connection

langgraph_graph = ModuleType("langgraph.graph")


class _DummyStateGraph:
    def __init__(self, *args: object, **kwargs: object) -> None:
        return

    def add_node(self, *args: object, **kwargs: object) -> None:
        return

    def add_edge(self, *args: object, **kwargs: object) -> None:
        return

    def add_conditional_edges(self, *args: object, **kwargs: object) -> None:
        return

    async def ainvoke(self, initial_state: object, *args: object, **kwargs: object) -> object:
        return initial_state


setattr(langgraph_graph, "END", "END")
setattr(langgraph_graph, "StateGraph", _DummyStateGraph)
sys.modules["langgraph.graph"] = langgraph_graph

workflow_router_stub = ModuleType("ml.domain.workflow.router")


async def _stub_workflow(payload: object):  # type: ignore[no-untyped-def]
    async def _empty_stream():  # pragma: no cover - dummy generator
        if False:
            yield {}

    return _empty_stream(), "general", None


async def _stub_workflow_collected(payload: object):  # type: ignore[no-untyped-def]
    return "", "general"


setattr(workflow_router_stub, "workflow", _stub_workflow)
setattr(workflow_router_stub, "workflow_collected", _stub_workflow_collected)
sys.modules["ml.domain.workflow.router"] = workflow_router_stub

workflow_package_stub = ModuleType("ml.domain.workflow")
setattr(workflow_package_stub, "router", workflow_router_stub)
sys.modules["ml.domain.workflow"] = workflow_package_stub

import importlib

app_module = importlib.import_module("ml.api.app")
from ml.api import app as create_app
from ml.api.external.websocket_client import GraphLogWebSocketClient
from ml.api.routes import workflow as workflow_routes
from ml.configs import LLMMode
from ml.domain.models.payload_data import Tag


class DummyGraphLogWebSocketClient(GraphLogWebSocketClient):
    def __init__(self) -> None:
        super().__init__(base_url="ws://test")

    async def connect(self, chat_id: int):  # type: ignore[override]
        return None

    async def close(self, chat_id: int) -> None:  # type: ignore[override]
        return None


class FailingGraphLogWebSocketClient(GraphLogWebSocketClient):
    def __init__(self) -> None:
        super().__init__(base_url="ws://test")

    async def connect(self, chat_id: int):  # type: ignore[override]
        msg = f"Failed to open websocket for chat {chat_id}"
        raise RuntimeError(msg)


_DEFAULT_CLIENT_SENTINEL: Literal["default"] = "default"


def _valid_payload() -> dict[str, object]:
    return {
        "messages": [{"role": "user", "content": "Hello"}],
        "chat_id": 1,
        "tag": Tag.General.value,
        "mode": "fast",
        "file_url": None,
        "is_voice": False,
        "profile": {
            "id": 1,
            "login": "tester",
            "username": "test-user",
            "user_info": "info",
            "business_info": "business",
            "additional_instructions": "none",
        },
    }


@contextmanager
def _build_test_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    graph_log_client: GraphLogWebSocketClient | None,
    workflow_collected_impl: Callable[[object], Awaitable[tuple[str, Tag]]],
    model_ready: bool,
) -> Iterator[TestClient]:
    async def _return_empty_list() -> list[str]:
        return []

    async def _noop_download(available_models: list[str], requested_models: list[str]) -> None:
        return None

    async def _noop_warmup() -> None:
        return None

    async def _init_graph_log_client() -> GraphLogWebSocketClient | None:
        return graph_log_client

    monkeypatch.setattr(workflow_routes, "workflow_collected", workflow_collected_impl)
    monkeypatch.setattr(app_module, "get_llm_mode", lambda: LLMMode.OLLAMA)
    monkeypatch.setattr(app_module, "fetch_available_models", _return_empty_list)
    monkeypatch.setattr(app_module, "get_models_from_env", _return_empty_list)
    monkeypatch.setattr(app_module, "download_missing_models", _noop_download)
    monkeypatch.setattr(app_module, "init_warmup_clients", _noop_warmup)
    monkeypatch.setattr(app_module, "clients_warmup", _noop_warmup)
    monkeypatch.setattr(app_module, "init_graph_log_client", _init_graph_log_client)

    app = create_app()

    with TestClient(app) as test_client:
        if not model_ready:
            test_client.app.state.model_ready = asyncio.Event()
        if graph_log_client is not None:
            test_client.app.state.graph_log_client = graph_log_client

        yield test_client


@pytest.fixture()
def test_client_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., ContextManager[TestClient]]:
    async def default_workflow_collected(payload: object) -> tuple[str, Tag]:
        return "Workflow output", Tag.General

    @contextmanager
    def _factory(
        graph_log_client: GraphLogWebSocketClient | None | Literal["default"] = (
            _DEFAULT_CLIENT_SENTINEL
        ),
        workflow_collected_impl: Callable[[object], Awaitable[tuple[str, Tag]]] = (
            default_workflow_collected
        ),
        model_ready: bool = True,
    ) -> Iterator[TestClient]:
        resolved_graph_client = (
            DummyGraphLogWebSocketClient()
            if graph_log_client is _DEFAULT_CLIENT_SENTINEL
            else graph_log_client
        )

        with _build_test_client(
            monkeypatch,
            graph_log_client=resolved_graph_client,
            workflow_collected_impl=workflow_collected_impl,
            model_ready=model_ready,
        ) as client:
            yield client

    return _factory

@pytest.fixture()
def client(test_client_factory: Callable[..., ContextManager[TestClient]]) -> Iterator[TestClient]:
    with test_client_factory() as default_client:
        yield default_client


def test_ping_endpoint_returns_pong(client: TestClient) -> None:
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_message_endpoint_returns_collected_response(client: TestClient) -> None:
    response = client.post("/message", json=_valid_payload())

    assert response.status_code == 200
    assert response.json() == {"content": "Workflow output", "tag": Tag.General.value}


def test_message_endpoint_returns_service_unavailable_when_models_not_ready(
    test_client_factory: Callable[..., ContextManager[TestClient]],
) -> None:
    with test_client_factory(model_ready=False) as test_client:
        response = test_client.post("/message", json=_valid_payload())

    assert response.status_code == 503
    assert response.json()["detail"] == "Models are still initialising"


def test_message_endpoint_returns_internal_error_when_graph_client_missing(
    test_client_factory: Callable[..., ContextManager[TestClient]],
) -> None:
    with test_client_factory(graph_log_client=None) as test_client:
        response = test_client.post("/message", json=_valid_payload())

    assert response.status_code == 500
    assert response.json()["detail"] == "Graph log client is not configured"


def test_message_endpoint_returns_bad_gateway_when_websocket_connect_fails(
    test_client_factory: Callable[..., ContextManager[TestClient]],
) -> None:
    failing_client = FailingGraphLogWebSocketClient()

    with test_client_factory(graph_log_client=failing_client) as test_client:
        response = test_client.post("/message", json=_valid_payload())

    assert response.status_code == 502
    assert response.json()["detail"] == "Graph log websocket connection failed"


def test_message_endpoint_rejects_invalid_payload(
    test_client_factory: Callable[..., ContextManager[TestClient]]
) -> None:
    invalid_payload = _valid_payload()
    invalid_payload["messages"] = [
        {"role": "assistant", "content": "first"},
        {"role": "assistant", "content": "second"},
    ]

    with test_client_factory() as test_client:
        response = test_client.post("/message", json=invalid_payload)

    assert response.status_code == 422
