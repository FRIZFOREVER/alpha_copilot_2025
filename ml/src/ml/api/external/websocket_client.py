from __future__ import annotations

import logging

from websockets.asyncio.client import ClientConnection, connect

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
