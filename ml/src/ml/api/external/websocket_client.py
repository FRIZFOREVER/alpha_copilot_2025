from __future__ import annotations

import json
import logging
from typing import ClassVar

from websockets.asyncio.client import ClientConnection, connect
from websockets.asyncio.connection import State

from ml.domain.models.graph_log import GraphLogMessage, PicsTags

logger = logging.getLogger(__name__)

GRAPH_LOG_SERVER_URL = "ws://app:8080"


def _normalize_backend_url(raw_backend_url: str) -> str:
    if not isinstance(raw_backend_url, str):
        raise TypeError("Backend url should be a string")

    if raw_backend_url.startswith("http://"):
        normalized = f"ws://{raw_backend_url[len('http://'):]}"
    elif raw_backend_url.startswith("https://"):
        normalized = f"wss://{raw_backend_url[len('https://'):]}"
    elif raw_backend_url.startswith(("ws://", "wss://")):
        normalized = raw_backend_url
    else:
        normalized = f"ws://{raw_backend_url}"

    if normalized.endswith("/"):
        return normalized[:-1]

    return normalized


def get_backend_url() -> str:
    return _normalize_backend_url(GRAPH_LOG_SERVER_URL)


class GraphLogWebSocketClient:
    _instance: ClassVar[GraphLogWebSocketClient | None] = None

    def __init__(self, base_url: str | None = None) -> None:
        if getattr(self, "_initialized", False):
            return

        raw_base_url = base_url if base_url is not None else get_backend_url()
        self.base_url = _normalize_backend_url(raw_base_url)
        self._connections: dict[int, ClientConnection] = {}
        self._initialized = True

    @classmethod
    def instance(cls, base_url: str | None = None) -> GraphLogWebSocketClient:
        if cls._instance is None:
            cls._instance = cls(base_url=base_url)
        return cls._instance

    def writer_url(self, chat_id: int) -> str:
        return f"{self.base_url}/graph_log_writer/{chat_id}"

    async def connect(self, chat_id: int) -> ClientConnection:
        connection = self._connections.get(chat_id)
        if connection is not None:
            connection_state = connection.state
            if connection_state is State.OPEN:
                logger.info(
                    "Reusing open graph log websocket connection for chat_id=%s (url=%s)",
                    chat_id,
                    self.writer_url(chat_id),
                )
                return connection
            if connection_state in (State.CLOSING, State.CLOSED):
                await connection.wait_closed()
                self._connections.pop(chat_id, None)
            else:
                logger.warning(
                    "Dropping graph log websocket connection for chat_id=%s due to unexpected state=%s",
                    chat_id,
                    connection_state,
                )
                await connection.close()
                await connection.wait_closed()
                self._connections.pop(chat_id, None)

        url = self.writer_url(chat_id)
        try:
            logger.info("Connecting to graph log websocket at %s", url)
            connection = await connect(
                url,
                additional_headers={
                    "Authorization": "Token secret_service",
                },
            )
            self._connections[chat_id] = connection
            return connection
        except Exception:
            logger.exception("Failed to connect to graph log websocket at %s", url)
            raise

    async def close(self, chat_id: int) -> None:
        connection = self._connections.pop(chat_id, None)
        if connection is None:
            return

        await connection.close()

    async def send_action(
        self, chat_id: int, *, tag: PicsTags, message: str, answer_id: int
    ) -> None:
        connection = await self.connect(chat_id)
        url = self.writer_url(chat_id)
        payload: GraphLogMessage = {"tag": tag, "answer_id": answer_id, "message": message}

        try:
            logger.info(
                "Sending graph log payload to %s: %s (connection_closed=%s)",
                url,
                payload,
                connection.state in (State.CLOSING, State.CLOSED),
            )
            await connection.send(json.dumps(payload, ensure_ascii=False))
            logger.info("Graph log payload sent to %s for chat_id=%s", url, chat_id)
        except Exception:
            logger.exception(
                "Failed to send graph log payload to %s for chat_id=%s: %s",
                url,
                chat_id,
                payload,
            )
            await self.close(chat_id)
            raise


async def init_graph_log_client(base_url: str | None = None) -> GraphLogWebSocketClient:
    logger.info("Initializing graph log WebSocket client")
    return GraphLogWebSocketClient.instance(base_url=base_url)


async def send_graph_log(*, chat_id: int, tag: PicsTags, message: str, answer_id: int) -> None:
    client = GraphLogWebSocketClient.instance()
    await client.send_action(chat_id=chat_id, tag=tag, message=message, answer_id=answer_id)
