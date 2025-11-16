import asyncio
import threading
from collections.abc import Callable, Iterator
from contextlib import suppress
from dataclasses import dataclass
from typing import TypeAlias

from ollama import ChatResponse

from ml.configs.message import RequestPayload, Tag


class StreamComplete:
    """Sentinel object indicating that the streaming workflow finished."""

    __slots__ = ()


@dataclass(slots=True)
class StreamError:
    """Wrapper for propagating exceptions through the streaming queue."""

    error: BaseException


STREAM_COMPLETE = StreamComplete()

StreamQueueItem: TypeAlias = ChatResponse | StreamError | StreamComplete


@dataclass(slots=True)
class AsyncStreamHandle:
    """Handle for coordinating async streaming work."""

    queue: asyncio.Queue[StreamQueueItem]
    worker_task: asyncio.Task[None]
    tag: Tag
    stop: Callable[[], None]


def workflow(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    from ml.agent.graph.pipeline import run_pipeline

    return run_pipeline(payload)


def workflow_collected(payload: RequestPayload) -> tuple[str, Tag]:
    tag: Tag
    stream: Iterator[ChatResponse]
    stream, tag = workflow(payload=payload)

    buffer_string: str = ""

    for chunk in stream:
        content: str | None = chunk.message.content
        if content:
            buffer_string += content

    return buffer_string, tag


async def workflow_async(payload: RequestPayload) -> tuple[Iterator[ChatResponse], Tag]:
    return await asyncio.to_thread(workflow, payload)


async def workflow_collected_async(payload: RequestPayload) -> tuple[str, Tag]:
    return await asyncio.to_thread(workflow_collected, payload)


async def async_stream_workflow(payload: RequestPayload) -> AsyncStreamHandle:
    """Stream workflow responses through a queue populated in a worker thread."""

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[StreamQueueItem] = asyncio.Queue()
    tag_future: asyncio.Future[Tag] = loop.create_future()
    stop_event: threading.Event = threading.Event()

    def _put_from_thread(item: StreamQueueItem) -> None:
        asyncio.run_coroutine_threadsafe(queue.put(item), loop).result()

    def _stop_worker() -> None:
        stop_event.set()

    def _run_stream() -> None:
        try:
            stream, tag = workflow(payload)
            loop.call_soon_threadsafe(tag_future.set_result, tag)
            for chunk in stream:
                if stop_event.is_set():
                    break
                _put_from_thread(chunk)
        except Exception as exc:  # pragma: no cover - exercised via queue propagation
            if not tag_future.done():
                loop.call_soon_threadsafe(tag_future.set_exception, exc)
            _put_from_thread(StreamError(error=exc))
            return

        _put_from_thread(STREAM_COMPLETE)

    async def _worker() -> None:
        await asyncio.to_thread(_run_stream)

    worker_task: asyncio.Task[None] = asyncio.create_task(_worker())

    try:
        tag = await tag_future
    except Exception:
        _stop_worker()
        with suppress(Exception):
            await worker_task
        raise

    return AsyncStreamHandle(queue=queue, worker_task=worker_task, tag=tag, stop=_stop_worker)
