"""Runtime feature flags for optional ML service behaviours."""
from __future__ import annotations

import os


def _get_bool_env(var_name: str, default: bool) -> bool:
    """Return the boolean value of an environment variable.

    Truthy values include ``1``, ``true``, ``yes`` and ``on`` (case-insensitive).
    Falsy values include ``0``, ``false``, ``no`` and ``off``. Missing variables
    fall back to ``default``.
    """

    value = os.getenv(var_name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    # Unrecognised values fall back to the provided default to avoid surprises.
    return default


PIPELINE_LOGGING_ENABLED: bool = _get_bool_env("PIPELINE_LOGGING_ENABLED", True)
"""When enabled, pipeline activity is written to a dedicated log handler."""
