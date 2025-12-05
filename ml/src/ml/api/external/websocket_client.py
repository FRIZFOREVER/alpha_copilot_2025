from __future__ import annotations

import json
import logging
from typing import ClassVar

from websockets.asyncio.client import ClientConnection, connect

from ml.domain.models.graph_log import GraphLogMessage, PicsTags

logger = logging.getLogger(__name__)

GRAPH_LOG_SERVER_URL = "ws://app:8080"


class GraphLogWebSocketClient:
    _instance: ClassVar[GraphLogWebSocketClient | None] = None

    def __init__(self, base_url: str = GRAPH_LOG_SERVER_URL) -> None:
        if getattr(self, "_initialized", False):
            return

        self.base_url = base_url
        self._initialized = True

    @classmethod
    def instance(cls, base_url: str = GRAPH_LOG_SERVER_URL) -> GraphLogWebSocketClient:
        if cls._instance is None:
            cls._instance = cls(base_url=base_url)
        return cls._instance

    def writer_url(self, chat_id: int) -> str:
        return f"{self.base_url}/graph_log_writer/{chat_id}"

    async def connect(self, chat_id: int) -> ClientConnection:
        url = self.writer_url(chat_id)
        try:
            logger.info("Connecting to graph log websocket at %s", url)
            return await connect(url)
        except Exception:
            logger.exception("Failed to connect to graph log websocket at %s", url)
            raise

    async def send_action(
        self, chat_id: int, *, tag: PicsTags, message: str, answer_id: int
    ) -> None:
        connection = await self.connect(chat_id)
        if not isinstance(connection, ClientConnection):
            raise TypeError("Graph log connection must be a websockets ClientConnection")

        payload: GraphLogMessage = {"tag": tag, "answer_id": answer_id, "message": message}

        try:
            await connection.send(json.dumps(payload, ensure_ascii=False))
        finally:
            await connection.close()


async def init_graph_log_client(base_url: str = GRAPH_LOG_SERVER_URL) -> GraphLogWebSocketClient:
    logger.info("Initializing graph log WebSocket client")
    return GraphLogWebSocketClient.instance(base_url=base_url)


async def send_graph_log(*, chat_id: int, tag: PicsTags, message: str, answer_id: int) -> None:
    client = GraphLogWebSocketClient.instance()
    await client.send_action(chat_id=chat_id, tag=tag, message=message, answer_id=answer_id)
