"""Конфигурация приложения"""

import os
import logging

logger = logging.getLogger(__name__)

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
