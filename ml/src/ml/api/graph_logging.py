"""Helpers for dispatching graph log events in the background."""

from __future__ import annotations

import asyncio
import logging
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Final

from ml.api.graph_history import GraphLogClient, PicsTags

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _GraphLogItem:
    tag: PicsTags
    answer_id: int
    message: str


_SHUTDOWN: Final[object] = object()

GraphLogContext = tuple["GraphLogDispatcher", int | None]
graph_log_context: ContextVar[GraphLogContext | None] = ContextVar(
    "graph_log_context", default=None
)


class GraphLogDispatcher:
    """Dispatch graph log events through an asyncio queue."""

    def __init__(self, loop: asyncio.AbstractEventLoop, client: GraphLogClient) -> None:
        self._loop = loop
        self._client = client
        self._queue: asyncio.Queue[object] = asyncio.Queue()

    def submit(self, tag: PicsTags, answer_id: int, message: str) -> None:
        """Enqueue a log event from any thread."""

        item = _GraphLogItem(tag=tag, answer_id=answer_id, message=message)
        self._loop.call_soon_threadsafe(self._queue.put_nowait, item)

    def stop(self) -> None:
        """Request graceful shutdown of the dispatcher."""

        self._loop.call_soon_threadsafe(self._queue.put_nowait, _SHUTDOWN)

    async def run(self) -> None:
        """Process queued log events until a shutdown sentinel is received."""

        while True:
            item = await self._queue.get()
            if item is _SHUTDOWN:
                break

            if isinstance(item, _GraphLogItem):
                try:
                    await self._client.send_log(
                        tag=item.tag, question_id=item.answer_id, message=item.message
                    )
                except Exception:
                    logger.exception("Failed to dispatch graph_log message")


def set_graph_log_context(
    dispatcher: GraphLogDispatcher, answer_id: int | None
) -> Token[GraphLogContext | None]:
    """Persist dispatcher context for the lifetime of the request."""

    return graph_log_context.set((dispatcher, answer_id))


def reset_graph_log_context(token: Token[GraphLogContext | None]) -> None:
    """Restore the previous graph log context."""

    graph_log_context.reset(token)


def send_graph_log(tag: PicsTags, message: str, answer_id: int | None = None) -> None:
    """Fire-and-forget helper for synchronous graph code."""

    context_value = graph_log_context.get()
    if context_value is None:
        return

    dispatcher, context_answer_id = context_value
    if dispatcher is None:
        return

    target_answer_id = answer_id if answer_id is not None else context_answer_id
    if target_answer_id is None:
        return

    dispatcher.submit(tag=tag, answer_id=target_answer_id, message=message)
