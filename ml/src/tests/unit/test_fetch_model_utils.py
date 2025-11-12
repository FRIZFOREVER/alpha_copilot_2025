import pytest

from ml.utils import fetch_model


class _AsyncTracker:
    def __init__(self):
        self.count = 0

    async def gather(self, *coroutines):
        self.count = len(coroutines)
        results = []
        for coroutine in coroutines:
            results.append(await coroutine)
        return results


@pytest.mark.asyncio
async def test_get_configured_model_ids_returns_unique_models(monkeypatch):
    monkeypatch.setattr(
        fetch_model,
        "list_configured_models",
        lambda: {"chat": " llama ", "embeddings": "", "reranker": "llama"},
    )

    assert fetch_model.get_configured_model_ids() == {"llama"}


@pytest.mark.asyncio
async def test_fetch_models_dispatches_parallel_pulls(monkeypatch):
    tracker = _AsyncTracker()
    pulled = []

    def fake_pull(model: str) -> None:
        pulled.append(model)

    monkeypatch.setattr(fetch_model, "get_configured_model_ids", lambda: {"beta", "alpha"})
    monkeypatch.setattr(fetch_model.ollama, "pull", fake_pull)
    monkeypatch.setattr(fetch_model.asyncio, "gather", tracker.gather)

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(fetch_model.asyncio, "to_thread", fake_to_thread)

    result = await fetch_model.fetch_models()

    assert tracker.count == 2
    assert sorted(pulled) == ["alpha", "beta"]
    assert result == {"alpha": True, "beta": True}


@pytest.mark.asyncio
async def test_pull_model_returns_false_on_failure(monkeypatch):
    def fake_pull(model: str) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(fetch_model.ollama, "pull", fake_pull)

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(fetch_model.asyncio, "to_thread", fake_to_thread)

    result = await fetch_model._pull_model("broken-model")

    assert result is False


@pytest.mark.asyncio
async def test_prune_unconfigured_models_deletes_extras(monkeypatch):
    tracker = _AsyncTracker()
    deleted = []

    monkeypatch.setattr(fetch_model, "get_configured_model_ids", lambda: {"keep"})

    def fake_list():
        return {"models": [{"name": "keep"}, {"name": "drop"}, {"model": "extra"}]}

    def fake_delete(model: str) -> None:
        deleted.append(model)

    monkeypatch.setattr(fetch_model.ollama, "list", fake_list)
    monkeypatch.setattr(fetch_model.ollama, "delete", fake_delete)
    monkeypatch.setattr(fetch_model.asyncio, "gather", tracker.gather)

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(fetch_model.asyncio, "to_thread", fake_to_thread)

    result = await fetch_model.prune_unconfigured_models()

    assert tracker.count == 2
    assert sorted(deleted) == ["drop", "extra"]
    assert result == {"drop": True, "extra": True}


@pytest.mark.asyncio
async def test_prune_unconfigured_models_propagates_listing_errors(monkeypatch):
    monkeypatch.setattr(fetch_model, "get_configured_model_ids", lambda: {"keep"})

    def failing_list():
        raise RuntimeError("cannot list")

    monkeypatch.setattr(fetch_model.ollama, "list", failing_list)

    def fail_delete(model: str) -> None:
        raise AssertionError("delete should not be called when listing fails")

    monkeypatch.setattr(fetch_model.ollama, "delete", fail_delete)

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(fetch_model.asyncio, "to_thread", fake_to_thread)

    with pytest.raises(RuntimeError, match="cannot list"):
        await fetch_model.prune_unconfigured_models()
