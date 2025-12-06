from __future__ import annotations

from collections.abc import AsyncIterator
import importlib
import sys
from typing import Any
import types

import pytest
from ollama._types import ChatResponse, Message
from ml.domain.models import ChatHistory, GraphState, MetaData, Message as DomainMessage
from ml.domain.models import ModelMode, Role, Tag, UserProfile


class StubPayload:
    def __init__(
        self,
        *,
        messages: ChatHistory,
        chat_id: int,
        tag: Tag,
        mode: ModelMode,
        file_url: str | None,
        is_voice: bool,
        profile: UserProfile,
    ) -> None:
        self.messages = messages
        self.chat_id = chat_id
        self.tag = tag
        self.mode = mode
        self.file_url = file_url
        self.is_voice = is_voice
        self.profile = profile


class StubPipeline:
    def __init__(self, result_state: Any) -> None:
        self.result_state = result_state
        self.calls: list[tuple[GraphState, dict[str, Any]]] = []

    async def ainvoke(self, state: GraphState, config: dict[str, Any]) -> Any:
        self.calls.append((state, config))
        return self.result_state


@pytest.fixture()
def router(monkeypatch: pytest.MonkeyPatch) -> Any:
    stub_message_payload_module = types.ModuleType("ml.api.schemas.message_payload")

    class MessagePayload:
        pass

    stub_message_payload_module.MessagePayload = MessagePayload
    stub_message_payload_module.Tag = Tag

    stub_schemas_module = types.ModuleType("ml.api.schemas")
    stub_schemas_module.MessagePayload = MessagePayload
    stub_schemas_module.Tag = Tag
    stub_api_module = types.ModuleType("ml.api")
    stub_api_module.schemas = stub_schemas_module

    stub_pipeline_module = types.ModuleType("ml.domain.workflow.agent.pipeline")

    def create_pipeline() -> Any:
        raise RuntimeError("Stub pipeline should be patched within tests")

    stub_pipeline_module.create_pipeline = create_pipeline

    monkeypatch.setitem(sys.modules, "ml.api", stub_api_module)
    monkeypatch.setitem(sys.modules, "ml.api.schemas", stub_schemas_module)
    monkeypatch.setitem(
        sys.modules, "ml.api.schemas.message_payload", stub_message_payload_module
    )
    monkeypatch.setitem(
        sys.modules, "ml.domain.workflow.agent.pipeline", stub_pipeline_module
    )
    monkeypatch.delitem(sys.modules, "ml.domain.workflow.router", raising=False)

    return importlib.import_module("ml.domain.workflow.router")


def _async_stream(values: list[Any]) -> AsyncIterator[Any]:
    async def _generator() -> AsyncIterator[Any]:
        for value in values:
            yield value

    return _generator()


def _build_payload(file_url: str | None = None) -> StubPayload:
    chat = ChatHistory(messages=[DomainMessage(id=1, role=Role.user, content="Hi")])

    return StubPayload(
        messages=chat,
        chat_id=1,
        tag=Tag.General,
        mode=ModelMode.Research,
        file_url=file_url,
        is_voice=False,
        profile=UserProfile(
            id=2,
            login="user",
            username="Test User",
            user_info="info",
            business_info="biz",
            additional_instructions="",
        ),
    )


def _base_state(
    *,
    output_stream: AsyncIterator[dict[str, Any]] | Any,
    meta_tag: Any = Tag.General,
    file_url: Any = None,
) -> GraphState:
    chat = ChatHistory(messages=[DomainMessage(id=1, role=Role.user, content="Hi")])
    if isinstance(meta_tag, Tag):
        meta = MetaData(is_voice=False, tag=meta_tag)
    else:
        meta = MetaData.model_construct(is_voice=False, tag=meta_tag)

    return GraphState.model_construct(
        chat_id=1,
        chat=chat,
        user=UserProfile(
            id=2,
            login="user",
            username="Test User",
            user_info="info",
            business_info="biz",
            additional_instructions="",
        ),
        meta=meta,
        file_url=file_url,
        model_mode=ModelMode.Research,
        voice_is_valid=None,
        final_prompt=None,
        output_stream=output_stream,
    )


@pytest.mark.anyio("asyncio")
async def test_workflow_accepts_graphstate(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_stream = _async_stream([{"text": "hello"}])
    result_state = _base_state(output_stream=output_stream, file_url="/tmp/file.txt")
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    stream, tag, file_url = await router.workflow(_build_payload(file_url="/tmp/file.txt"))

    assert stream is output_stream
    assert tag is Tag.General
    assert file_url == "/tmp/file.txt"
    assert pipeline.calls[0][1]["run_name"] == "main_pipeline"


@pytest.mark.anyio("asyncio")
async def test_workflow_accepts_dict_state(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_stream = _async_stream([{"text": "hello"}])
    state_dict = _base_state(output_stream=output_stream)
    pipeline = StubPipeline(state_dict.model_dump())
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    stream, tag, file_url = await router.workflow(_build_payload())

    assert isinstance(stream, AsyncIterator)
    assert tag is Tag.General
    assert file_url is None


@pytest.mark.anyio("asyncio")
async def test_workflow_raises_for_unknown_state_type(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipeline = StubPipeline(result_state=123)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    with pytest.raises(TypeError):
        await router.workflow(_build_payload())


@pytest.mark.anyio("asyncio")
async def test_workflow_requires_output_stream(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_state = _base_state(output_stream=None)
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    with pytest.raises(RuntimeError):
        await router.workflow(_build_payload())


@pytest.mark.anyio("asyncio")
async def test_workflow_validates_output_stream_type(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_state = _base_state(output_stream="not a stream")
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    with pytest.raises(TypeError):
        await router.workflow(_build_payload())


@pytest.mark.anyio("asyncio")
async def test_workflow_validates_meta_tag(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_state = _base_state(output_stream=_async_stream([{"text": "hello"}]), meta_tag="tag")
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    with pytest.raises(TypeError):
        await router.workflow(_build_payload())


@pytest.mark.anyio("asyncio")
async def test_workflow_validates_file_url(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_state = _base_state(output_stream=_async_stream([{"text": "hello"}]), file_url=123)
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    with pytest.raises(TypeError):
        await router.workflow(_build_payload())


@pytest.mark.anyio("asyncio")
async def test_workflow_collected_streams_chunks(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    chat_response = ChatResponse(
        model="model",
        message=Message(role="assistant", thinking="T", content="C"),
    )
    output_stream = _async_stream([
        chat_response,
        {"choices": [{"delta": {"content": "D"}}]},
        "E",
        b"F",
    ])
    result_state = _base_state(output_stream=output_stream)
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    collected, tag = await router.workflow_collected(_build_payload())

    assert collected == "TCDEF"
    assert tag is Tag.General


@pytest.mark.anyio("asyncio")
async def test_workflow_collected_rejects_unsupported_chunk(
    router: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_stream = _async_stream([object()])
    result_state = _base_state(output_stream=output_stream)
    pipeline = StubPipeline(result_state)
    monkeypatch.setattr(router, "create_pipeline", lambda: pipeline)

    with pytest.raises(TypeError):
        await router.workflow_collected(_build_payload())
