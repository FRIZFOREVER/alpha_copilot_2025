from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any, TypeVar, cast

from ollama import AsyncClient  # type: ignore[reportUnknownVariableType]
from pydantic import BaseModel

from ml.configs import EmbeddingClientSettings, ReasoningClientSettings
from ml.domain.models import ChatHistory

T = TypeVar("T", bound=BaseModel)

logger: logging.Logger = logging.getLogger(__name__)


class ReasoningModelClient:
    def __init__(self, settings: ReasoningClientSettings | None = None) -> None:
        if settings is None:
            logging.debug("Automatically defining settings for Reasoner client")
            settings = ReasoningClientSettings()
        self.settings: ReasoningClientSettings = settings

        logger.debug(
            "initiated Reasoning client with: \n%s", self.settings.model_dump_json(indent=2)
        )
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


class EmbeddingModelClient:
    def __init__(self, settings: EmbeddingClientSettings | None = None) -> None:
        if settings is None:
            logging.debug("Automatically defining settings for Embedding client")
            settings = EmbeddingClientSettings()
        self.settings: EmbeddingClientSettings = settings
        logger.debug(
            "initiated Embedding client with: \n%s", self.settings.model_dump_json(indent=2)
        )

        # Async Ollama client (same pattern as ReasoningModelClient)
        self.client: Any = AsyncClient(
            host=self.settings.base_url,
        )

        # TODO: Plan for empty embeddings env workaround

    async def call(self, content: str, **kwargs: Any) -> list[float]:
        """
        Async call for generating a single embedding vector.

        Returns a single embedding vector (list[float]) for the given content.
        """
        logger.debug(
            "Calling Embedder with content length=%d",
            len(content),
        )

        try:
            response: dict[str, Any] = await self.client.embed(
                model=self.settings.model,
                input=content,
                options=self.settings.options.model_dump() | kwargs,
                keep_alive=self.settings.keep_alive,
            )
        except Exception:
            logger.exception("Error while calling Ollama embed (async)")
            raise

        # Ollama embed is guaranteed to return: {"embeddings": list[list[float]]}
        embeddings = cast(list[list[float]], response["embeddings"])

        if not embeddings:
            raise RuntimeError("Got empty embeddings from embedding model")

        return embeddings[0]
