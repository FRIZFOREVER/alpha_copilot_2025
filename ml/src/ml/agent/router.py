from typing import Any, Dict

from ml.agent.calls.model_calls import make_client, _ReasoningModelClient
from ml.configs.model_config import ModelSettings
from ml.configs.message import Message


_MODEL_CLIENTS: Dict[str, Any] = {}


def workflow(payload: Dict[str, Any]) -> str:
    client: _ReasoningModelClient = _MODEL_CLIENTS["chat"]
    answer: Message = client.call(payload["messages"])
    return answer.content

def chat_completition():
    pass

async def init_models() -> Dict[str, Any]:
    modes = ("chat", "reranker", "embeddings")
    global _MODEL_CLIENTS
    _MODEL_CLIENTS = {mode: make_client(ModelSettings(api_mode=mode)) for mode in modes}
    return _MODEL_CLIENTS
