# from ml.utils.formats import _rstrip_slash
from ml.configs.model_config import ModelSettings
from ml.configs.message import Message
from ollama import chat, ChatResponse, embed
from typing import Union, List, Dict


class _ReasoningModelClient:
    """Thin wrapper around `ollama.chat` for conversational reasoning models."""

    def __init__(self, settings: ModelSettings):
        self.s: ModelSettings = settings

    def call(self, messages: List[Dict[str, str]]) -> Message:
        response: ChatResponse = chat(
            model=self.s.model,
            messages=messages,
            options={
                "temperature": self.s.temperature,
                "top_p": self.s.top_p,
            }
            )
        answer: Message = Message(role=response.message.role,
                content=response.message.content
                )
        return answer

class _RerankModelClient:
    """Utility wrapper for using chat models as lightweight rerankers."""

    def __init__(self, settings: ModelSettings):
        self.s: ModelSettings = settings

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
        # return True if field is 'yes', otherwise return 'no'
        return True if response.message.content['label'] == 'yes' else False 
    
    def call_batch(self, messages: List[List[Dict[str,str]]])  -> List[bool]:
        return [self.call(item) for item in messages]


class _EmbeddingModelClient:
    """Batch-friendly helper for producing embeddings via `ollama.embed`."""

    def __init__(self, settings: ModelSettings):
        self.s: ModelSettings = settings
    
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
