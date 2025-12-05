from __future__ import annotations

import json
import logging

from websockets.asyncio.client import ClientConnection, connect

from ml.domain.models.graph_log import GraphLogMessage, PicsTags

logger = logging.getLogger(__name__)

GRAPH_LOG_SERVER_URL = "ws://app:8080"


class GraphLogWebSocketClient:
    def __init__(self, base_url: str = GRAPH_LOG_SERVER_URL) -> None:
        self.base_url = base_url

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


async def init_graph_log_client() -> GraphLogWebSocketClient:
    logger.info("Initializing graph log WebSocket client")
    return GraphLogWebSocketClient()


async def send_graph_log(
    connection: ClientConnection, *, tag: PicsTags, message: str, answer_id: int
) -> None:
    if not isinstance(connection, ClientConnection):
        raise TypeError("Graph log connection must be a websockets ClientConnection")

    payload: GraphLogMessage = {"tag": tag, "answer_id": answer_id, "message": message}
    await connection.send(json.dumps(payload, ensure_ascii=False))
