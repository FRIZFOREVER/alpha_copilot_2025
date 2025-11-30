import logging
import os
from typing import Final

from uvicorn.logging import DefaultFormatter

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
    return _LOG_LEVEL_MAP.get(raw, logging.INFO)


def configure_logging() -> None:
    """Apply a minimal logging setup based on ML_LOG_LEVEL."""
    level = get_log_level()
    ml_logger = logging.getLogger("ml")
    ml_logger.setLevel(level)

    handler_exists = any(isinstance(handler, logging.StreamHandler) for handler in ml_logger.handlers)
    if not handler_exists:
        handler = logging.StreamHandler()
        handler.setFormatter(DefaultFormatter(fmt="%(levelprefix)s %(message)s", use_colors=False))
        handler.setLevel(level)
        ml_logger.addHandler(handler)
