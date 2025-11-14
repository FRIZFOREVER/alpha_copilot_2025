import logging
from collections.abc import Iterator
from typing import TypeVar

from ml.configs.message import ChatHistory
from ml.configs.model_config import EmbeddingClientSettings, ReasoningClientSettings
from ollama import ChatResponse, chat, embed
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class ReasoningModelClient:
    def __init__(self, settings: ReasoningClientSettings = ReasoningClientSettings()):
        self.settings: ReasoningClientSettings = settings

    def call(self, messages: ChatHistory, **kwargs) -> str:
        logger.info("Calling Reasoner with messages as payload: %s", messages.messages_list())
        return chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
            stream=False,
        ).message.content

    def stream(self, messages: ChatHistory, **kwargs) -> Iterator[ChatResponse]:
        return chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
            stream=True,
        )

    def call_structured(self, messages: ChatHistory, output_schema: type[T], **kwargs) -> T:
        response: ChatResponse = chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            format=output_schema.model_json_schema(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
        )

        raw = response.message.content

        try:
            return output_schema.model_validate_json(raw)
        except Exception as exc:
            logger.warning("FAILED TO PARSE STRUCTURED OUTPUT")
            raise ValueError("Structured response did not match the expected schema") from exc


class EmbeddingModelClient:
    def __init__(self, settings: EmbeddingClientSettings = EmbeddingClientSettings()):
        self.settings: EmbeddingClientSettings = settings

    def call(self, content: str, **kwargs) -> list[float]:
        response = embed(
            model=self.settings.model,
            input=content,
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
        )
        return response["embeddings"][0]
