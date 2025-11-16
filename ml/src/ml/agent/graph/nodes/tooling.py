"""Shared helpers for research tool graph nodes."""

from collections.abc import Mapping

_KNOWN_INPUT_KEYS: tuple[str, ...] = (
    "query",
    "input",
    "input_text",
    "request",
    "prompt",
)


def select_primary_input(arguments: Mapping[str, str]) -> str:
    """Return the most relevant argument that can serve as a tool input preview."""

    for key in _KNOWN_INPUT_KEYS:
        candidate = arguments.get(key)
        if candidate is None:
            continue
        if candidate == "":
            continue
        return candidate
    return ""
