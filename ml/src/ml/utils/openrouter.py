from __future__ import annotations

from typing import Any

from ml.configs import LLMMode

OPENROUTER_PROVIDER_BODY: dict[str, dict[str, object]] = {
    "provider": {
        "only": ["novita/fp8"],
        "allow_fallbacks": False,
        "require_parameters": True,
    }
}


def apply_openrouter_provider(response_kwargs: dict[str, Any], mode: LLMMode) -> None:
    """Inject the OpenRouter provider constraint when applicable."""

    if mode is not LLMMode.OPENROUTER:
        return

    response_kwargs["extra_body"] = OPENROUTER_PROVIDER_BODY
