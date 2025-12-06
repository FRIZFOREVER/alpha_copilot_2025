"""Конфигурация приложения"""

import os
import logging

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
if OLLAMA_HOST.endswith("/v1"):
    OLLAMA_HOST = OLLAMA_HOST[:-3]
elif OLLAMA_HOST.endswith("/"):
    OLLAMA_HOST = OLLAMA_HOST[:-1]

DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2:3b")
