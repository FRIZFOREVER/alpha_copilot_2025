"""Utility to configure Python logging from the shared YAML configuration."""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml

__all__ = ["configure_logging"]

_CONFIGURED = False
_CONFIG_PATH = Path(__file__).resolve().parent / "logging.yaml"


def configure_logging() -> None:
    """Load the shared logging configuration so app logs are routed consistently."""

    global _CONFIGURED
    if _CONFIGURED:
        return

    if not _CONFIG_PATH.is_file():
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning(
            "Logging config %s missing, falling back to basic logging", _CONFIG_PATH
        )
        _CONFIGURED = True
        return

    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        logging.config.dictConfig(config)
    except Exception:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).exception(
            "Failed to configure logging from %s; using basic config", _CONFIG_PATH
        )
    finally:
        _CONFIGURED = True
