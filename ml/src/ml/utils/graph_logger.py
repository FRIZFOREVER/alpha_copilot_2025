"""WebSocket клиент для отправки graph_log на бэкенд."""

import asyncio
import json
import logging
import os
from typing import Optional

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)


class GraphLogClient:
    """Клиент для отправки graph_log через WebSocket."""

    def __init__(self, backend_url: str, chat_id: str):
        """
        Инициализация клиента.

        Args:
            backend_url: URL бэкенда (например, "ws://localhost:8080")
            chat_id: ID чата
        """
        self.backend_url = backend_url.rstrip("/")
        self.chat_id = chat_id
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False

    async def connect(self) -> bool:
        """
        Подключение к WebSocket endpoint бэкенда.

        Returns:
            True если подключение успешно, False в противном случае
        """
        try:
            ws_url = f"{self.backend_url}/graph_log_writer/{self.chat_id}"
            logger.info(f"Подключение к WebSocket: {ws_url}")
            self.ws = await websockets.connect(ws_url)
            self.connected = True
            logger.info(f"WebSocket подключен для чата {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к WebSocket: {e}")
            self.connected = False
            return False

    async def send_log(self, tag: str, question_id: int, message: str) -> bool:
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

        try:
            log_message = {
                "tag": tag,
                "answer_id": question_id,  # Передаем question_id, бэкенд получит answer_id по нему
                "message": message,
            }
            await self.ws.send(json.dumps(log_message))
            logger.debug(f"Отправлен graph_log: {log_message}")
            return True
        except (ConnectionClosed, WebSocketException) as e:
            logger.error(f"Ошибка отправки graph_log: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке graph_log: {e}")
            return False

    async def close(self) -> None:
        """Закрытие WebSocket соединения."""
        if self.ws:
            try:
                await self.ws.close()
                logger.info(f"WebSocket соединение закрыто для чата {self.chat_id}")
            except Exception as e:
                logger.error(f"Ошибка при закрытии WebSocket: {e}")
            finally:
                self.ws = None
                self.connected = False


def get_backend_url() -> str:
    """
    Получение URL бэкенда из переменной окружения.
    Автоматически определяет Docker окружение и преобразует http/https в ws/wss.

    Returns:
        URL бэкенда для WebSocket (ws:// или wss://)
    """
    # Проверяем, работаем ли мы в Docker
    has_dockerenv = os.path.exists("/.dockerenv")
    has_docker_env = bool(os.getenv("DOCKER_ENV"))
    is_docker = has_dockerenv or has_docker_env

    # Приоритет: переменная окружения > автоматическое определение
    backend_url_env = os.getenv("BACKEND_URL")
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

    # Преобразуем http:// в ws:// для WebSocket
    if backend_url.startswith("http://"):
        backend_url = backend_url.replace("http://", "ws://")
    elif backend_url.startswith("https://"):
        backend_url = backend_url.replace("https://", "wss://")
    elif not backend_url.startswith("ws://") and not backend_url.startswith("wss://"):
        # Если протокол не указан, добавляем ws://
        backend_url = f"ws://{backend_url}"

    logger.debug(f"Финальный backend_url для WebSocket: {backend_url}")
    return backend_url
