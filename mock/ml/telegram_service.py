"""
Сервис для работы с Telegram Bot API
"""

import os
import json
import logging
import httpx
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("TELEGRAM_DATA_DIR", "/app/data"))
TOKENS_FILE = DATA_DIR / "telegram_tokens.json"


class TelegramService:
    """Сервис для работы с Telegram Bot API"""

    TELEGRAM_API_URL = "https://api.telegram.org/bot"

    def __init__(self):
        self._ensure_tokens_file()

    def _ensure_tokens_file(self):
        """Создает файл для хранения токенов, если его нет"""
        tokens_dir = TOKENS_FILE.parent
        tokens_dir.mkdir(parents=True, exist_ok=True)
        if not TOKENS_FILE.exists():
            with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_tokens(self) -> Dict[str, Dict[str, Any]]:
        """Загружает токены из файла"""
        try:
            if TOKENS_FILE.exists():
                with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
            return {}

    def _save_tokens(self, tokens: Dict[str, Dict[str, Any]]):
        """Сохраняет токены в файл"""
        try:
            with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
            raise

    def save_token(
        self, user_id: str, bot_token: str, chat_id: Optional[str] = None
    ) -> bool:
        """
        Сохраняет токен бота и chat_id для пользователя

        Args:
            user_id: ID пользователя в системе
            bot_token: Токен Telegram бота
            chat_id: ID чата для отправки сообщений (опционально)

        Returns:
            True если токен валидный и сохранен
        """
        try:
            if not self._validate_token(bot_token):
                logger.error(f"Invalid bot token for user {user_id}")
                return False

            tokens = self._load_tokens()
            tokens[user_id] = {
                "bot_token": bot_token,
                "chat_id": chat_id,
                "connected": True,
            }
            self._save_tokens(tokens)
            logger.info(f"Token saved for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving token for user {user_id}: {e}")
            return False

    def _validate_token(self, bot_token: str) -> bool:
        """Проверяет валидность токена бота"""
        try:
            url = f"{self.TELEGRAM_API_URL}{bot_token}/getMe"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("ok", False)
                return False
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False

    def get_token(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получает сохраненный токен для пользователя"""
        tokens = self._load_tokens()
        return tokens.get(user_id)

    def is_connected(self, user_id: str) -> bool:
        """Проверяет, подключен ли Telegram для пользователя"""
        token_data = self.get_token(user_id)
        return token_data is not None and token_data.get("connected", False)

    def disconnect(self, user_id: str) -> bool:
        """Отключает Telegram для пользователя"""
        try:
            tokens = self._load_tokens()
            if user_id in tokens:
                tokens[user_id]["connected"] = False
                self._save_tokens(tokens)
                logger.info(f"Telegram disconnected for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error disconnecting Telegram for user {user_id}: {e}")
            return False

    async def send_message(
        self, user_id: str, text: str, chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Отправляет сообщение в Telegram

        Args:
            user_id: ID пользователя в системе
            text: Текст сообщения
            chat_id: ID чата (если не указан, используется сохраненный)

        Returns:
            Результат отправки сообщения
        """
        token_data = self.get_token(user_id)
        if not token_data or not token_data.get("connected"):
            return {
                "success": False,
                "error": "Telegram not connected for this user",
            }

        bot_token = token_data.get("bot_token")
        target_chat_id = chat_id or token_data.get("chat_id")

        if not bot_token:
            return {"success": False, "error": "Bot token not found"}

        if not target_chat_id:
            return {"success": False, "error": "Chat ID not specified"}

        try:
            url = f"{self.TELEGRAM_API_URL}{bot_token}/sendMessage"
            payload = {
                "chat_id": target_chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response_data = response.json()

                if response.status_code == 200 and response_data.get("ok"):
                    logger.info(f"Message sent to Telegram for user {user_id}")
                    return {
                        "success": True,
                        "message_id": response_data.get("result", {}).get("message_id"),
                    }
                else:
                    error_description = response_data.get(
                        "description", "Unknown error"
                    )
                    logger.error(
                        f"Failed to send message to Telegram: {error_description}"
                    )
                    return {
                        "success": False,
                        "error": error_description,
                    }
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return {"success": False, "error": str(e)}

    def get_bot_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о боте"""
        token_data = self.get_token(user_id)
        if not token_data or not token_data.get("connected"):
            return None

        bot_token = token_data.get("bot_token")
        if not bot_token:
            return None

        try:
            url = f"{self.TELEGRAM_API_URL}{bot_token}/getMe"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return data.get("result")
                return None
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None
