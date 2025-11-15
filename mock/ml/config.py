"""Конфигурация приложения"""

import os
import logging

logger = logging.getLogger(__name__)

# Ollama конфигурация
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
if OLLAMA_HOST.endswith("/v1"):
    OLLAMA_HOST = OLLAMA_HOST[:-3]
elif OLLAMA_HOST.endswith("/"):
    OLLAMA_HOST = OLLAMA_HOST[:-1]

# Telegram конфигурация
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")

# Модель по умолчанию
DEFAULT_MODEL = "gpt-oss:120b-cloud"
