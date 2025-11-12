# from ml.utils.formats import _rstrip_slash
import json
from typing import Any, Dict, Iterator, List, Type, Union

from ollama import ChatResponse, chat, embed
from pydantic import BaseModel

from ml.configs.model_config import EmbeddingClientSettings, ReasoningClientSettings
from ml.configs.message import ChatHistory

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
                        output_schema: Dict[str, Any],
                        **kwargs
                        ) -> Union[Dict[str, Any], BaseModel]:
        
        response: ChatResponse = chat(
            model=self.settings.model,
            messages=messages,
            format=output_schema, # pass via BaseModel.model_json_schema()
            options=self.settings.options | kwargs,
            keep_alive=self.settings.keep_alive,
        )
        
        content = response.message.content
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the string
                # Some models might return text with JSON embedded
                parsed = {"error": "Invalid JSON response", "raw": content}
        else:
            parsed = content

        # If output_schema is a Pydantic model class, return parsed model instance
        if isinstance(output_schema, type) and issubclass(output_schema, BaseModel):
            try:
                return output_schema.model_validate(parsed)
            except Exception as e:
                raise ValueError(f"Failed to validate structured output: {e}") from e

        return parsed

class _EmbeddingModelClient(ModelClient):
    """Batch-friendly helper for producing embeddings via `ollama.embed`."""

    def call(self, content: str) -> List[float]:
        response = embed(
            model=self.settings.model,
            input=content,
            keep_alive=self.settings.keep_alive,
        )
        return response["embeddings"][0]

    def call_batch(self, inputs: List[str]) -> List[List[float]]:
        if not isinstance(inputs, list):
            raise TypeError("Embedding client expects input text as a list of strings.")

        batch_size = max(1, self.settings.embed_batch_size)
        embeddings: List[List[float]] = []

        for idx in range(0, len(inputs), batch_size):
            batch_inputs = inputs[idx : idx + batch_size]
            response = embed(
                model=self.settings.model,
                input=batch_inputs,
                keep_alive=self.settings.keep_alive,
            )
            embeddings.extend(response["embeddings"])

        return embeddings


_CLIENTS = {
    "chat": _ReasoningModelClient,
    "embeddings": _EmbeddingModelClient,
}


# Function for export. Takes ModelSettings.api_mode to determinate model
def make_client(settings: ModelSettings) -> Union[_ReasoningModelClient, _EmbeddingModelClient]:
    return _CLIENTS[settings.api_mode](settings)
