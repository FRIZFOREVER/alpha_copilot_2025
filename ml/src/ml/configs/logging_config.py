import logging
import os
from typing import Final

logger = logging.getLogger(__name__)

_LOG_LEVEL_MAP: Final[dict[str | None, int]] = {
    None: logging.INFO,
    "": logging.INFO,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def get_log_level() -> int:
    """Return numeric logging level based on ML_LOG_LEVEL env var."""
    raw = os.getenv("ML_LOG_LEVEL")
    logging.info("Logging level: %s", raw)
    return _LOG_LEVEL_MAP.get(raw, logging.INFO)
