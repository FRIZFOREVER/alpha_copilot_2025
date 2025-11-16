"""WebSocket клиент для отправки graph_log на бэкенд."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import TypedDict

import websockets
from websockets.client import ClientConnection
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

DOCKER_ENV_KEY = "DOCKER_ENV"
BACKEND_URL_KEY = "BACKEND_URL"
DOCKERENV_PATH = Path("/.dockerenv")


class PicsTags(str, Enum):
    Web = "web"
    Think = "think"
    Mic = "mic"


class GraphLogMessage(TypedDict):
    tag: PicsTags
    answer_id: int
    message: str


def get_backend_url() -> str:
    """
    Получение URL бэкенда из переменной окружения.
    Автоматически определяет Docker окружение и преобразует http/https в ws/wss.

    Returns:
        URL бэкенда для WebSocket (ws:// или wss://)
    """
    # Проверяем, работаем ли мы в Docker
    has_dockerenv = DOCKERENV_PATH.exists()
    has_docker_env = bool(os.getenv(DOCKER_ENV_KEY))
    is_docker = has_dockerenv or has_docker_env

    # Приоритет: переменная окружения > автоматическое определение
    backend_url_env = os.getenv(BACKEND_URL_KEY)
    if backend_url_env:
        backend_url = backend_url_env
        logger.info(f"Используется BACKEND_URL из переменной окружения: {backend_url}")
    else:
        # Автоматическое определение
        default_backend = "http://app:8080" if is_docker else "http://localhost:8080"
        backend_url = default_backend
        logger.info(
            f"BACKEND_URL не установлен. Определение окружения: "
            f"is_docker={is_docker} (/.dockerenv={has_dockerenv}, DOCKER_ENV={has_docker_env}), "
            f"используется: {backend_url}"
        )

    backend_url = backend_url.strip()

    # Преобразуем http:// в ws:// для WebSocket и добавляем ws://, если схема не указана
    if backend_url.startswith("http://"):
        backend_url = f"ws://{backend_url.removeprefix('http://')}"
    elif backend_url.startswith("https://"):
        backend_url = f"wss://{backend_url.removeprefix('https://')}"
    elif not backend_url.startswith(("ws://", "wss://")):
        backend_url = f"ws://{backend_url}"

    logger.debug(f"Финальный backend_url для WebSocket: {backend_url}")
    return backend_url


@dataclass
class GraphLogClient:
    """Клиент для отправки graph_log через WebSocket."""

    backend_url: str
    chat_id: str
    ws: ClientConnection | None = field(init=False, default=None)
    connected: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self.backend_url = self.backend_url.rstrip("/")

    @property
    def writer_url(self) -> str:
        """Возвращает конечную точку бэкенда для graph_log."""
        return f"{self.backend_url}/graph_log_writer/{self.chat_id}"

    async def __aenter__(self) -> GraphLogClient:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    def _reset_connection(self) -> None:
        """Сбрасывает состояние подключения."""
        self.ws = None
        self.connected = False

    async def connect(self) -> bool:
        """
        Подключение к WebSocket endpoint бэкенда.

        Returns:
            True если подключение успешно, False в противном случае
        """
        try:
            logger.info(f"Подключение к WebSocket: {self.writer_url}")
            self.ws = await websockets.connect(self.writer_url)
            self.connected = True
            logger.info(f"WebSocket подключен для чата {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к WebSocket: {e}")
            self._reset_connection()
            return False

    async def send_log(self, tag: PicsTags, question_id: int, message: str) -> bool:
        """
        Отправка лога через WebSocket.

        Args:
            tag: Тег лога
            question_id: ID вопроса (из последнего сообщения с role="user")
            message: Сообщение лога

        Returns:
            True если отправка успешна, False в противном случае
        """
        if not self.connected or not self.ws:
            logger.warning("WebSocket не подключен, пропускаем отправку лога")
            return False

        log_message: GraphLogMessage = {
            "tag": tag,
            "answer_id": question_id,  # Передаем question_id, бэкенд получит answer_id по нему
            "message": message,
        }

        try:
            await self.ws.send(json.dumps(log_message))
            logger.debug(f"Отправлен graph_log: {log_message}")
            return True
        except (ConnectionClosed, WebSocketException) as e:
            logger.error(f"Ошибка отправки graph_log: {e}")
            self._reset_connection()
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке graph_log: {e}")
            return False

    async def close(self) -> None:
        """Закрытие WebSocket соединения."""
        if not self.ws:
            return

        try:
            await self.ws.close()
            logger.info(f"WebSocket соединение закрыто для чата {self.chat_id}")
        except Exception as e:
            logger.error(f"Ошибка при закрытии WebSocket: {e}")
        finally:
            self._reset_connection()
