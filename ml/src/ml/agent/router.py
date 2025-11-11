from typing import Any, Dict, Iterator, Union
import json
import logging

from ml.agent.calls.model_calls import make_client, _ReasoningModelClient
from ml.configs.model_config import ModelSettings
from ml.configs.message import Message
from ml.agent.graph.pipeline import run_pipeline, run_pipeline_stream
from ollama import ChatResponse

logger = logging.getLogger("app.router")

_MODEL_CLIENTS: Dict[str, Any] = {}


def workflow(payload: Dict[str, Any], streaming=False) -> Union[str, Iterator[ChatResponse]]:
    """Main workflow function that routes to LangGraph pipeline."""
    client: _ReasoningModelClient = _MODEL_CLIENTS["chat"]
    if streaming:
        answer: Iterator[ChatResponse] = chat_completion_stream(client=client, payload=payload)
    else:
        answer: str = chat_completion(client=client, payload=payload)
    return answer
    
def chat_completion(client: _ReasoningModelClient, payload: Dict[str, Any]) -> str:
    """Run pipeline and return final answer as string."""
    messages = payload.get("messages", [])
    final_state = run_pipeline(client=client, messages=messages)
    if final_state is not None:
        try:
            state_payload = final_state.model_dump()
        except AttributeError:
            state_payload = final_state
    else:
        state_payload = None
    logger.info("Final state:\n%s", json.dumps(state_payload, ensure_ascii=False, indent=2))
    if final_state and final_state.final_answer:
        return final_state.final_answer
    else:
        return "Извините, не удалось сгенерировать ответ."

def chat_completion_stream(client: _ReasoningModelClient, payload: Dict[str, Any]) -> Iterator[ChatResponse]:
    """Run pipeline and stream final answer generation."""
    messages = payload.get("messages", [])
    return run_pipeline_stream(client=client, messages=messages)
    

async def init_models() -> Dict[str, Any]:
    modes = ("chat", "reranker", "embeddings")
    global _MODEL_CLIENTS
    _MODEL_CLIENTS = {mode: make_client(ModelSettings(api_mode=mode)) for mode in modes}
    return _MODEL_CLIENTS
