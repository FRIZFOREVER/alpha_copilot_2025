# from ml.utils.formats import _rstrip_slash
from typing import Iterator, List, TypeVar

from ollama import ChatResponse, chat, embed
from pydantic import BaseModel

from ml.configs.model_config import EmbeddingClientSettings, ReasoningClientSettings
from ml.configs.message import ChatHistory

T = TypeVar("T", bound=BaseModel)

class ReasoningModelClient:
    def __init__(self, settings: ReasoningClientSettings):
        self.settings: ReasoningClientSettings = settings

    def call(self, messages: ChatHistory, **kwargs) -> str:
        return chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
            stream=False
        ).message.content

    def stream(self, messages: ChatHistory, **kwargs) -> Iterator[ChatResponse]:
        return chat(
            model=self.settings.model,
            messages=messages.messages_list(),
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
            stream=True,
        )
    
    def call_structured(self, 
                        messages: ChatHistory, 
                        output_schema: type[T],
                        **kwargs
                        ) -> T:
        
        response: ChatResponse = chat(
            model=self.settings.model,
            messages=messages,
            format=output_schema.model_json_schema(),
            options=self.settings.options | kwargs,
            keep_alive=self.settings.keep_alive,
        )
        
        raw = response.message.content

        try:
            return output_schema.model_validate_json(raw)
        except Exception as exc:
            raise ValueError("Structured response did not match the expected schema") from exc

class EmbeddingModelClient(EmbeddingClientSettings):

    def __init__(self, settings: EmbeddingClientSettings):
        self.settings: EmbeddingClientSettings = settings

    def call(self, content: str, **kwargs) -> List[float]:
        response = embed(
            model=self.settings.model,
            input=content,
            options=self.settings.options.model_dump() | kwargs,
            keep_alive=self.settings.keep_alive,
        )
        return response["embeddings"][0]