"""Utilities for structured logging within the agent pipeline."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Mapping, Optional

from ml.configs.runtime_flags import PIPELINE_LOGGING_ENABLED

if False:  # pragma: no cover - typing imports
    from ml.agent.graph.state import GraphState


PIPELINE_LOGGER_NAME = "app.pipeline"


def get_pipeline_logger() -> logging.Logger:
    """Return the logger configured for pipeline activity."""

    return logging.getLogger(PIPELINE_LOGGER_NAME)


def _serialise(value: Any) -> Any:
    """Best-effort conversion into JSON-friendly structures."""

    if isinstance(value, Mapping):
        return {str(key): _serialise(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialise(item) for item in value]
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:  # pragma: no cover - defensive fallback
            return repr(value)
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:  # pragma: no cover - defensive fallback
            return repr(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _extract_identifiers(
    state: "GraphState | None", config: Optional[Mapping[str, Any]]
) -> Dict[str, Any]:
    identifiers: Dict[str, Any] = {}

    configurable: Mapping[str, Any] = {}
    if config:
        configurable = config.get("configurable") or {}

    for key in ("thread_id", "checkpoint_ns", "checkpoint_id"):
        value = None
        if isinstance(configurable, Mapping):
            value = configurable.get(key)
        if state is not None and not value:
            value = getattr(state, key, None)
        elif state is not None and getattr(state, key, None):
            # Prefer identifiers explicitly stored on the state object.
            value = getattr(state, key)
        if value:
            identifiers[key] = value

    if state is not None:
        mode = getattr(state, "mode", None)
        if mode:
            identifiers["mode"] = mode
        research_iteration = getattr(state, "research_iteration", None)
        if research_iteration is not None:
            identifiers["research_iteration"] = research_iteration

    return identifiers


def log_pipeline_event(
    event: str,
    *,
    message: Optional[str] = None,
    state: "GraphState | None" = None,
    config: Optional[Mapping[str, Any]] = None,
    level: int = logging.INFO,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Log a structured pipeline record if logging is enabled."""

    if not PIPELINE_LOGGING_ENABLED:
        return

    logger = get_pipeline_logger()
    if logger.disabled:
        return

    payload: Dict[str, Any] = {"event": event}
    if message:
        payload["message"] = message

    payload.update(_extract_identifiers(state, config))

    if extra:
        payload.update(_serialise(extra))

    try:
        serialised = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):  # pragma: no cover - defensive fallback
        serialised = repr(payload)

    logger.log(level, serialised)
