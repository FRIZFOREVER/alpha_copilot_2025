from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any, TypeVar

from ollama import AsyncClient  # type: ignore[reportUnknownVariableType]
from pydantic import BaseModel

from ml.configs import ReasoningClientSettings
from ml.domain.models import ChatHistory

T = TypeVar("T", bound=BaseModel)

logger: logging.Logger = logging.getLogger(__name__)


class ReasoningModelClient:
    def __init__(self, settings: ReasoningClientSettings | None = None) -> None:
        if settings is None:
            settings = ReasoningClientSettings()
        self.settings: ReasoningClientSettings = settings

        # Async Ollama client (OpenAI-compatible base_url assumed in settings)
        self.client: Any = AsyncClient(
            host=self.settings.base_url,
        )

    async def call(self, messages: ChatHistory, **kwargs: Any) -> str:
        """Async non-streaming call."""
        logger.debug(
            "Calling Reasoner with messages as payload: %s",
            messages.model_dump_json(indent=2),
        )

        try:
            response: dict[str, Any] = await self.client.chat(
                model=self.settings.model,
                messages=messages.model_dump_chat(),
                options=self.settings.options.model_dump() | kwargs,
                keep_alive=self.settings.keep_alive,
                stream=False,
            )
            content: str | None = response["message"]["content"]

            if content is None:
                raise RuntimeError("Got None from chat completion without stream function")

            return content

        except Exception:
            logger.exception("Error while calling Ollama chat (async)")
            raise

    async def stream(
        self,
        messages: ChatHistory,
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Async streaming call.

        Yields raw chunks from AsyncClient.chat(stream=True),
        suitable for SSE / websockets.
        """
        stream = await self.client.chat(
            model=self.settings.model,
            messages=messages.model_dump_chat(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
            stream=True,
        )

        async for chunk in stream:
            yield chunk

    async def call_structured(
        self,
        messages: ChatHistory,
        output_schema: type[T],
        **kwargs: Any,
    ) -> T:
        """
        Async call that asks the model to return JSON matching output_schema.
        """
        response: dict[str, Any] = await self.client.chat(
            model=self.settings.model,
            messages=messages.model_dump_chat(),
            format=output_schema.model_json_schema(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
        )

        raw: str | None = response["message"]["content"]

        if raw is None:
            raise RuntimeError("Got None from chat completion with structured output")

        try:
            return output_schema.model_validate_json(raw)
        except Exception as exc:
            logger.exception("FAILED TO PARSE STRUCTURED OUTPUT")
            raise ValueError("Structured response did not match the expected schema") from exc
