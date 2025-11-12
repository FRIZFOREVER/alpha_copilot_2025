# from ml.utils.formats import _rstrip_slash
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Type, Union

from ollama import ChatResponse, chat, embed
from pydantic import BaseModel

from ml.configs.model_config import ModelSettings
from ml.configs.message import Message

logger = logging.getLogger(__name__)



class ModelClient(ABC):
    def __init__(self, settings: ModelSettings):
        self.s: ModelSettings = settings
    
    @abstractmethod
    def call(self, messages: Any) -> Message:
        pass
    

class _ReasoningModelClient(ModelClient):
    """Thin wrapper around `ollama.chat` for conversational reasoning models."""

    def call(self, messages: List[Dict[str, str]]) -> Message:
        response: ChatResponse = chat(
            model=self.s.model,
            messages=messages,
            options={
                "temperature": self.s.temperature,
                "top_p": self.s.top_p,
            },
            keep_alive=self.s.keep_alive,
        )
        return Message(role=response.message.role, content=response.message.content)

    def stream(self, messages: List[Dict[str, str]]) -> Iterator[ChatResponse]:
        return chat(
            model=self.s.model,
            messages=messages,
            options={
                "temperature": self.s.temperature,
                "top_p": self.s.top_p,
            },
            stream=True,
            keep_alive=self.s.keep_alive,
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
            model=self.s.model,
            messages=messages,
            format=schema,
            options={
                "temperature": self.s.temperature,
                "top_p": self.s.top_p,
            },
            keep_alive=self.s.keep_alive,
        )
        
        # Parse response content
        content = response.message.content
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the string
                # Some models might return text with JSON embedded
                logger.warning(f"Failed to parse JSON from response: {content[:100]}")
                parsed = {"error": "Invalid JSON response", "raw": content}
        else:
            parsed = content
        
        # If output_schema is a Pydantic model class, return parsed model instance
        if isinstance(output_schema, type) and issubclass(output_schema, BaseModel):
            try:
                return output_schema.model_validate(parsed)
            except Exception as e:
                logger.error(f"Failed to validate structured output: {e}")
                raise
        
        return parsed

class _RerankModelClient(ModelClient):
    """Utility wrapper for using chat models as lightweight rerankers."""

    # WARNING: If you want to get score, we should switch this model to vLLM serving and take logits 
    # on Yes/No probability
    # Default ollama serving doesn't support logits parsing
    def call(self, messages: List[Dict[str, str]]) -> bool:
        response: ChatResponse = chat(
            model=self.s.model,
            messages=messages,
            format=self.s.rerank_json_schema,
            options={
                "temperature": self.s.temperature,
                "top_p": self.s.top_p,
            },
            keep_alive=self.s.keep_alive,
        )
        
        content = response.message.content
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                raise ValueError(f"Rerank model returned non-JSON content: {response.message.content!r}")

        label = content.get("label")
        if label not in {"yes", "no"}:
            raise ValueError(f"Unexpected label '{label}' from rerank model")

        return label == "yes"
        
        content = response.message.content

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(
                    "Rerank model returned non-JSON response, defaulting to False: %s",
                    content,
                )
                return False

        if not isinstance(content, dict):
            logger.warning(
                "Rerank model response has unexpected type %s, defaulting to False",
                type(content).__name__,
            )
            return False

        label = content.get("label")
        if not isinstance(label, str):
            logger.warning("Rerank model response missing 'label', defaulting to False")
            return False

        normalized_label = label.strip().lower()
        if normalized_label == "yes":
            return True

        if normalized_label != "no":
            logger.warning(
                "Rerank model response has unexpected label '%s', defaulting to False",
                label,
            )

        return False
    
    def call_batch(self, messages: List[List[Dict[str,str]]])  -> List[bool]:
        return [self.call(item) for item in messages]


class _EmbeddingModelClient(ModelClient):
    """Batch-friendly helper for producing embeddings via `ollama.embed`."""

    def call(self, content: str) -> List[float]:
        response = embed(
            model=self.s.model,
            input=content,
            keep_alive=self.s.keep_alive,
        )
        return response["embeddings"][0]

    def call_batch(self, inputs: List[str]) -> List[List[float]]:
        if not isinstance(inputs, list):
            raise TypeError("Embedding client expects input text as a list of strings.")

        batch_size = max(1, self.s.embed_batch_size)
        embeddings: List[List[float]] = []

        for idx in range(0, len(inputs), batch_size):
            batch_inputs = inputs[idx : idx + batch_size]
            response = embed(
                model=self.s.model,
                input=batch_inputs,
                keep_alive=self.s.keep_alive,
            )
            embeddings.extend(response["embeddings"])

        return embeddings


_CLIENTS = {
    "chat": _ReasoningModelClient,
    "embeddings": _EmbeddingModelClient,
    "reranker": _RerankModelClient,
}


# Function for export. Takes ModelSettings.api_mode to determinate model
def make_client(settings: ModelSettings) -> Union[_ReasoningModelClient, 
                                                  _EmbeddingModelClient, 
                                                  _RerankModelClient]:
    return _CLIENTS[settings.api_mode](settings)
