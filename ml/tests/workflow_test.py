import asyncio
from collections.abc import AsyncIterator
import sys
import types

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

langgraph_module = types.ModuleType("langgraph")
langgraph_graph_module = types.ModuleType("langgraph.graph")
duckduckgo_module = types.ModuleType("duckduckgo_search")
bs4_module = types.ModuleType("bs4")


class _DummyStateGraph:
    def __init__(self, *_: object, **__: object) -> None:
        return

    def add_node(self, *_: object, **__: object) -> None:
        return

    def add_edge(self, *_: object, **__: object) -> None:
        return

    def add_conditional_edges(self, *_: object, **__: object) -> None:
        return

    def set_entry_point(self, *_: object, **__: object) -> None:
        return

    def compile(self) -> "_DummyStateGraph":
        return self


langgraph_graph_module.END = "END"
langgraph_graph_module.StateGraph = _DummyStateGraph


class _DummyDDGS:
    def __init__(self, *_: object, **__: object) -> None:
        return

    def text(self, *_: object, **__: object) -> list[str]:
        return []


duckduckgo_module.DDGS = _DummyDDGS


class _DummyBeautifulSoup:
    def __init__(self, *_: object, **__: object) -> None:
        return

    def get_text(self, **__: object) -> str:
        return ""


bs4_module.BeautifulSoup = _DummyBeautifulSoup

sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", langgraph_graph_module)
sys.modules.setdefault("duckduckgo_search", duckduckgo_module)
sys.modules.setdefault("bs4", bs4_module)

from ml.api import app as create_app
from ml.api.routes import workflow as workflow_routes
from ml.api.schemas import MessagePayload
from ml.domain.models import ChatHistory, Message, ModelMode, Role, Tag, UserProfile


@pytest.fixture()
def fastapi_app() -> FastAPI:
    return create_app()


def test_health_route(fastapi_app: FastAPI) -> None:
    assert str(fastapi_app.url_path_for("message_stream")) == "/message_stream"


def test_message_stream_sets_tag_header(
    fastapi_app: FastAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _run() -> None:
        async def _dummy_output_stream() -> AsyncIterator[dict[str, str]]:
            yield {"message": "test"}

        async def _dummy_workflow(_: MessagePayload) -> tuple[AsyncIterator[dict[str, str]], Tag]:
            return _dummy_output_stream(), Tag.Law

        fastapi_app.state.model_ready = asyncio.Event()
        fastapi_app.state.model_ready.set()

        monkeypatch.setattr(workflow_routes, "workflow", _dummy_workflow)

        payload = MessagePayload(
            messages=ChatHistory(messages=[Message(role=Role.user, content="hello")]),
            chat_id=1,
            tag=Tag.Empty,
            mode=ModelMode.Fast,
            file_url="",
            is_voice=False,
            profile=UserProfile(
                id=1,
                login="user-login",
                username="User Name",
                user_info="",
                business_info="",
                additional_instructions="",
            ),
        )

        transport = ASGITransport(app=fastapi_app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/message_stream",
                json=payload.model_dump(mode="json"),
            )

        assert response.status_code == 200
        assert response.headers.get("X-Tag") == Tag.Law.value

    asyncio.run(_run())
