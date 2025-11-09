from typing import Any, Dict, Iterator, Union

from ml.agent.calls.model_calls import make_client, _ReasoningModelClient
from ml.configs.model_config import ModelSettings
from ml.configs.message import Message
from ollama import ChatResponse


_MODEL_CLIENTS: Dict[str, Any] = {}


def workflow(payload: Dict[str, Any], streaming=False) -> Union[str, Iterator[ChatResponse]]:
    client: _ReasoningModelClient = _MODEL_CLIENTS["chat"]
    if streaming:
        answer: Iterator[ChatResponse] = chat_completion_stream(client=client, payload=payload)
    else:
        answer: str = chat_completion(client=client, payload=payload)
    return answer
    
def chat_completion(client: _ReasoningModelClient, payload: Dict[str, Any]) -> str:
    answer: Message = client.call(payload["messages"])
    return answer.content

def chat_completion_stream(client: _ReasoningModelClient, payload: Dict[str, Any]) -> Iterator[ChatResponse]:
    return client.stream(payload["messages"])
    

async def init_models() -> Dict[str, Any]:
    modes = ("chat", "reranker", "embeddings")
    global _MODEL_CLIENTS
    _MODEL_CLIENTS = {mode: make_client(ModelSettings(api_mode=mode)) for mode in modes}
    return _MODEL_CLIENTS
