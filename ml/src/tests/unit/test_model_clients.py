from typing import Any, Dict, List

import pytest

from ml.agent.calls.model_calls import (
    _EmbeddingModelClient,
    _ReasoningModelClient,
)
from ml.configs.model_config import ModelSettings
from ml.utils.warmup import warmup_models


class _DummyMessage:
    def __init__(self, content: str) -> None:
        self.role = "assistant"
        self.content = content


class _DummyResponse:
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


def _chat_stub_factory(calls: List[Dict[str, Any]]):
    def _chat_stub(**kwargs: Any):
        calls.append(kwargs)
        if kwargs.get("stream"):
            return iter([])
        return _DummyResponse("{\"label\": \"yes\"}")

    return _chat_stub


def _embed_stub_factory(calls: List[Dict[str, Any]]):
    def _embed_stub(**kwargs: Any):
        calls.append(kwargs)
        user_input = kwargs["input"]
        if isinstance(user_input, list):
            return {"embeddings": [[0.0] for _ in user_input]}
        return {"embeddings": [[0.0]]}

    return _embed_stub


def test_reasoning_client_passes_keep_alive(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[Dict[str, Any]] = []
    monkeypatch.setattr("ml.agent.calls.model_calls.chat", _chat_stub_factory(calls))

    settings = ModelSettings(api_mode="chat", model="chat-model", keep_alive="45m")
    client = _ReasoningModelClient(settings)

    client.call([{"role": "user", "content": "hi"}])
    list(client.stream([{"role": "user", "content": "hi"}]))
    client.call_structured([{"role": "user", "content": "hi"}], {"type": "object"})

    assert [call["keep_alive"] for call in calls] == ["45m", "45m", "45m"]


def test_embedding_client_passes_keep_alive(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[Dict[str, Any]] = []
    monkeypatch.setattr("ml.agent.calls.model_calls.embed", _embed_stub_factory(calls))

    settings = ModelSettings(api_mode="embeddings", model="embed-model", keep_alive="5m")
    client = _EmbeddingModelClient(settings)

    client.call("warm")
    client.call_batch(["first", "second"])

    assert len(calls) == 2
    assert all(call["keep_alive"] == "5m" for call in calls)


@pytest.mark.asyncio
async def test_warmup_models_runs_reasoning_last(monkeypatch: pytest.MonkeyPatch) -> None:
    chat_calls: List[Dict[str, Any]] = []
    embed_calls: List[Dict[str, Any]] = []

    monkeypatch.setattr("ml.agent.calls.model_calls.chat", _chat_stub_factory(chat_calls))
    monkeypatch.setattr("ml.agent.calls.model_calls.embed", _embed_stub_factory(embed_calls))

    order: List[str] = []

    async def fake_to_thread(func, *args, **kwargs):
        order.append(func.__self__.s.api_mode)
        return func(*args, **kwargs)

    monkeypatch.setattr("ml.utils.warmup.asyncio.to_thread", fake_to_thread)

    reasoning_settings = ModelSettings(api_mode="chat", model="chat-model", keep_alive="30m")
    embedding_settings = ModelSettings(api_mode="embeddings", model="embed-model", keep_alive="10m")

    clients = [
        _ReasoningModelClient(reasoning_settings),
        _EmbeddingModelClient(embedding_settings),
    ]

    await warmup_models(clients)

    assert order[-1] == "chat"
    assert "chat" not in order[:-1]
    assert embed_calls  # ensure embedding warmup executed
    assert chat_calls  # ensure reasoning warmup executed
