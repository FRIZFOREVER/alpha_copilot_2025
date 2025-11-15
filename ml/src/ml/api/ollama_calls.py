import logging
from collections.abc import Iterator
from typing import Any, TypeVar

from ollama import ChatResponse, EmbedResponse, chat, embed  # type: ignore
from pydantic import BaseModel

from ml.configs.message import ChatHistory
from ml.configs.model_config import EmbeddingClientSettings, ReasoningClientSettings

T = TypeVar("T", bound=BaseModel)

logger: logging.Logger = logging.getLogger(__name__)


class ReasoningModelClient:
    def __init__(self, settings: ReasoningClientSettings | None = None) -> None:
        if settings is None:
            settings = ReasoningClientSettings()
        self.settings: ReasoningClientSettings = settings

    def call(self, messages: ChatHistory, **kwargs: Any) -> str:
        logger.info(
            "Calling Reasoner with messages as payload: %s",
            messages.messages_list(),
        )

        try:
            response: ChatResponse = chat(
                model=self.settings.model,
                messages=messages.messages_list(),
                options=self.settings.options.model_dump() | kwargs,
                keep_alive=self.settings.keep_alive,
                stream=False,
            )
            content: str | None = response.message.content

            if content is None:
                raise RuntimeError("Got None from chat completion without stream function")

            return content

        except Exception:
            logger.exception("Error while calling Ollama chat")
            raise

    def stream(self, messages: ChatHistory, **kwargs: Any) -> Iterator[ChatResponse]:
        return chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
            stream=True,
        )

    def call_structured(self, messages: ChatHistory, output_schema: type[T], **kwargs: Any) -> T:
        response: ChatResponse = chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            format=output_schema.model_json_schema(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
        )

        raw: str | None = response.message.content

        if raw is None:
            raise RuntimeError("Got None from chat completion with  function")

        try:
            return output_schema.model_validate_json(raw)
        except Exception as exc:
            logger.exception("FAILED TO PARSE STRUCTURED OUTPUT")
            raise ValueError("Structured response did not match the expected schema") from exc


class EmbeddingModelClient:
    def __init__(self, settings: EmbeddingClientSettings | None = None) -> None:
        if settings is None:
            settings = EmbeddingClientSettings()
        self.settings: EmbeddingClientSettings = settings

    def call(self, content: str, **kwargs: Any) -> list[float]:
        response: EmbedResponse = embed(
            model=self.settings.model,
            input=content,
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
        )
        return response["embeddings"][0]
