from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any, ClassVar, TypeVar, cast

from ollama import AsyncClient
from openai import AsyncOpenAI
from pydantic import BaseModel

from ml.configs import (
    EmbeddingClientSettings,
    LLMMode,
    ReasoningClientSettings,
    get_llm_mode,
    get_provider_api_key,
    get_provider_base_url,
)
from ml.domain.models import ChatHistory

T = TypeVar("T", bound=BaseModel)

logger: logging.Logger = logging.getLogger(__name__)


class ReasoningModelClient:
    _instance: ClassVar[ReasoningModelClient | None] = None

    def __init__(self, settings: ReasoningClientSettings | None = None) -> None:
        self.mode: LLMMode = get_llm_mode()
        provider_base_url: str | None = None
        provider_api_key: str | None = None

        if self.mode is not LLMMode.OLLAMA:
            provider_base_url = get_provider_base_url(self.mode)
            provider_api_key = get_provider_api_key(self.mode)

        self.settings: ReasoningClientSettings = self._resolve_settings(
            settings, provider_base_url
        )

        logger.debug(
            "initiated Reasoning client with mode=%s and settings: \n%s",
            self.mode.value,
            self.settings.model_dump_json(indent=2),
        )

        if self.mode is LLMMode.OLLAMA:
            self.client: Any = AsyncClient(host=self.settings.base_url)
        else:
            self.client = AsyncOpenAI(base_url=provider_base_url, api_key=provider_api_key)

    @classmethod
    def instance(
        cls,
        settings: ReasoningClientSettings | None = None,
    ) -> ReasoningModelClient:
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    async def call(self, messages: ChatHistory, **kwargs: Any) -> str:
        """Async non-streaming call."""
        logger.debug(
            "Calling Reasoner with messages as payload: %s",
            messages.model_dump_json(indent=2),
        )

        if self.mode is LLMMode.OLLAMA:
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

        max_tokens = _limit_tokens(self.settings.options.num_predict)

        response_kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages.model_dump_chat(),
            "temperature": self.settings.options.temperature,
            "top_p": self.settings.options.top_p,
            "stream": False,
        }

        if max_tokens is not None:
            response_kwargs["max_tokens"] = max_tokens

        response_kwargs.update(kwargs)

        response = await self.client.chat.completions.create(**response_kwargs)

        content = response.choices[0].message.content

        if content is None:
            raise RuntimeError("Got None from chat completion without stream function")

        return content

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
        if self.mode is LLMMode.OLLAMA:
            stream = await self.client.chat(
                model=self.settings.model,
                messages=messages.model_dump_chat(),
                options=self.settings.options.model_dump() | kwargs,
                keep_alive=self.settings.keep_alive,
                stream=True,
            )

            async for chunk in stream:
                yield chunk
            return

        max_tokens = _limit_tokens(self.settings.options.num_predict)

        response_kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages.model_dump_chat(),
            "temperature": self.settings.options.temperature,
            "top_p": self.settings.options.top_p,
            "stream": True,
        }

        if max_tokens is not None:
            response_kwargs["max_tokens"] = max_tokens

        response_kwargs.update(kwargs)

        stream = await self.client.chat.completions.create(**response_kwargs)

        async for chunk in stream:
            yield chunk.model_dump()

    async def call_structured(
        self,
        messages: ChatHistory,
        output_schema: type[T],
        **kwargs: Any,
    ) -> T:
        """
        Async call that asks the model to return JSON matching output_schema.
        """
        if self.mode is LLMMode.OLLAMA:
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
        else:
            max_tokens = _limit_tokens(self.settings.options.num_predict)

            response_kwargs: dict[str, Any] = {
                "model": self.settings.model,
                "messages": messages.model_dump_chat(),
                "temperature": self.settings.options.temperature,
                "top_p": self.settings.options.top_p,
                "response_format": {"type": "json_object"},
                "stream": False,
            }

            if max_tokens is not None:
                response_kwargs["max_tokens"] = max_tokens

            response_kwargs.update(kwargs)

            response = await self.client.chat.completions.create(**response_kwargs)

            raw = response.choices[0].message.content

            if raw is None:
                raise RuntimeError("Got None from chat completion with structured output")

        try:
            return output_schema.model_validate_json(raw)
        except Exception as exc:
            logger.exception("FAILED TO PARSE STRUCTURED OUTPUT")
            raise ValueError("Structured response did not match the expected schema") from exc

    @staticmethod
    def _resolve_settings(
        settings: ReasoningClientSettings | None, provider_base_url: str | None
    ) -> ReasoningClientSettings:
        if settings is None:
            if provider_base_url is None:
                return ReasoningClientSettings()

            return ReasoningClientSettings(base_url=provider_base_url)

        if provider_base_url is None or settings.base_url:
            return settings

        return settings.model_copy(update={"base_url": provider_base_url})


class EmbeddingModelClient:
    _instance: ClassVar[EmbeddingModelClient | None] = None

    def __init__(self, settings: EmbeddingClientSettings | None = None) -> None:
        self.mode: LLMMode = get_llm_mode()
        provider_base_url: str | None = None
        provider_api_key: str | None = None

        if self.mode is not LLMMode.OLLAMA:
            provider_base_url = get_provider_base_url(self.mode)
            provider_api_key = get_provider_api_key(self.mode)

        self.settings: EmbeddingClientSettings = self._resolve_settings(
            settings, provider_base_url
        )
        logger.debug(
            "initiated Embedding client with mode=%s and settings: \n%s",
            self.mode.value,
            self.settings.model_dump_json(indent=2),
        )

        # Async Ollama client (same pattern as ReasoningModelClient)
        if self.mode is LLMMode.OLLAMA:
            self.client: Any = AsyncClient(host=self.settings.base_url)
        else:
            self.client = AsyncOpenAI(base_url=provider_base_url, api_key=provider_api_key)

    @classmethod
    def instance(
        cls,
        settings: EmbeddingClientSettings | None = None,
    ) -> EmbeddingModelClient:
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

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
            if self.mode is LLMMode.OLLAMA:
                response: dict[str, Any] = await self.client.embed(
                    model=self.settings.model,
                    input=content,
                    options=self.settings.options.model_dump() | kwargs,
                    keep_alive=self.settings.keep_alive,
                )
                embeddings = cast(list[list[float]], response["embeddings"])
            else:
                response = await self.client.embeddings.create(
                    model=self.settings.model,
                    input=content,
                    **kwargs,
                )
                embeddings = cast(list[float], response.data[0].embedding)
        except Exception:
            logger.exception("Error while calling embedding provider (async)")
            raise

        if not embeddings:
            raise RuntimeError("Got empty embeddings from embedding model")

        if self.mode is LLMMode.OLLAMA:
            return embeddings[0]

        return cast(list[float], embeddings)

    @staticmethod
    def _resolve_settings(
        settings: EmbeddingClientSettings | None, provider_base_url: str | None
    ) -> EmbeddingClientSettings:
        if settings is None:
            if provider_base_url is None:
                return EmbeddingClientSettings()

            return EmbeddingClientSettings(base_url=provider_base_url)

        if provider_base_url is None or settings.base_url:
            return settings

        return settings.model_copy(update={"base_url": provider_base_url})


def _limit_tokens(num_predict: int) -> int | None:
    if num_predict == -1:
        return None

    return num_predict
