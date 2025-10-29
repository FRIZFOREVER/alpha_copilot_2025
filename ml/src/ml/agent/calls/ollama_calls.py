# from ml.utils.formats import _rstrip_slash
from ml.configs.model_config import ModelSettings
from ollama import chat, embed
from typing import Union, List, Dict


class _ReasoningModelClient:
    def __init__(self, settings: ModelSettings):
        self.s: ModelSettings = settings

    def call(self, messages: List[Dict[str, str]]):
        chat(model=self.s.model,
             messages=messages)

class _RerankModelClient:
    def __init__(self, settings: ModelSettings):
        self.s = settings

class _EmbeddingModelClient:
    def __init__(self, settings: ModelSettings):
        self.s = settings


_CLIENTS = {
    "chat": _ReasoningModelClient,
    "embeddings": _EmbeddingModelClient,
    "reranker": _RerankModelClient,
}


def make_client(settings: ModelSettings) -> Union[_ReasoningModelClient, 
                                                  _EmbeddingModelClient, 
                                                  _RerankModelClient]:
    return _CLIENTS[settings.api_mode](settings)