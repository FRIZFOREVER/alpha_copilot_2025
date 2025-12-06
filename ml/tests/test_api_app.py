import asyncio
import sys
from types import ModuleType

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

@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    async def fake_workflow_collected(payload: object) -> tuple[str, Tag]:
        return "Workflow output", Tag.General

    async def _return_empty_list() -> list[str]:
        return []

    async def _noop_download(available_models: list[str], requested_models: list[str]) -> None:
        return None

    async def _noop_warmup() -> None:
        return None

    async def _init_graph_log_client() -> GraphLogWebSocketClient:
        return DummyGraphLogWebSocketClient()

    monkeypatch.setattr(workflow_routes, "workflow_collected", fake_workflow_collected)
    monkeypatch.setattr(app_module, "get_llm_mode", lambda: LLMMode.OLLAMA)
    monkeypatch.setattr(app_module, "fetch_available_models", _return_empty_list)
    monkeypatch.setattr(app_module, "get_models_from_env", _return_empty_list)
    monkeypatch.setattr(app_module, "download_missing_models", _noop_download)
    monkeypatch.setattr(app_module, "init_warmup_clients", _noop_warmup)
    monkeypatch.setattr(app_module, "clients_warmup", _noop_warmup)
    monkeypatch.setattr(app_module, "init_graph_log_client", _init_graph_log_client)

    app = create_app()
    app.state.model_ready = asyncio.Event()
    app.state.model_ready.set()

    with TestClient(app) as test_client:
        yield test_client


def test_ping_endpoint_returns_pong(client: TestClient) -> None:
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_message_endpoint_returns_collected_response(client: TestClient) -> None:
    payload = {
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

    response = client.post("/message", json=payload)

    assert response.status_code == 200
    assert response.json() == {"content": "Workflow output", "tag": Tag.General.value}
