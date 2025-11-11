# from ml.utils.formats import _rstrip_slash
from abc import ABC, abstractmethod
import json
from ml.configs.model_config import ModelSettings
from ml.configs.message import Message
from ollama import chat, ChatResponse, embed
from typing import Any, Union, List, Dict, Iterator



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
        )

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
            }
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
    def call_batch(self, messages: List[List[Dict[str,str]]])  -> List[bool]:
        return [self.call(item) for item in messages]


class _EmbeddingModelClient(ModelClient):
    """Batch-friendly helper for producing embeddings via `ollama.embed`."""

    def call(self, content: str) -> List[float]:
        response = embed(model=self.s.model, input=content)
        return response["embeddings"][0]

    def call_batch(self, inputs: List[str]) -> List[List[float]]:
        if not isinstance(inputs, list):
            raise TypeError("Embedding client expects input text as a list of strings.")

        batch_size = max(1, self.s.embed_batch_size)
        embeddings: List[List[float]] = []

        for idx in range(0, len(inputs), batch_size):
            batch_inputs = inputs[idx : idx + batch_size]
            response = embed(model=self.s.model, input=batch_inputs)
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
