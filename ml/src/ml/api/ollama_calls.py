# from ml.utils.formats import _rstrip_slash
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Type, Union

from ollama import ChatResponse, chat, embed
from pydantic import BaseModel

from ml.configs.model_config import ModelSettings
from ml.configs.message import Message



class ModelClient(ABC):
    def __init__(self, settings: ModelSettings):
        self.settings: ModelSettings = settings
    
    @abstractmethod
    def call(self, messages: Any) -> Message:
        pass
    

class _ReasoningModelClient(ModelClient):
    """Thin wrapper around `ollama.chat` for conversational reasoning models."""

    def call(self, messages: List[Dict[str, str]]) -> Message:
        response: ChatResponse = chat(
            model=self.settings.model,
            messages=messages,
            options={
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
            },
            keep_alive=self.settings.keep_alive,
        )
        return Message(role=response.message.role, content=response.message.content)

    def stream(self, messages: List[Dict[str, str]]) -> Iterator[ChatResponse]:
        return chat(
            model=self.settings.model,
            messages=messages,
            options={
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
            },
            stream=True,
            keep_alive=self.settings.keep_alive,
        )
    
    def call_structured(
        self, 
        messages: List[Dict[str, str]], 
        output_schema: Union[Dict[str, Any], Type[BaseModel]]
    ) -> Union[Dict[str, Any], BaseModel]:
        """
        Call model with structured output format.
        
        Args:
            messages: List of messages in Ollama format
            output_schema: Either a JSON schema dict or a Pydantic model class
            
        Returns:
            Parsed structured output (dict if schema provided, Pydantic model if model class provided)
        """
        # Convert Pydantic model to JSON schema if needed
        if isinstance(output_schema, type) and issubclass(output_schema, BaseModel):
            schema = output_schema.model_json_schema()
        else:
            schema = output_schema
        
        response: ChatResponse = chat(
            model=self.settings.model,
            messages=messages,
            format=schema,
            options={
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
            },
            keep_alive=self.settings.keep_alive,
        )
        
        # Parse response content
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
