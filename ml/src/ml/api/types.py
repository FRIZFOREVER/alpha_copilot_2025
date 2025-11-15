# ml/api/types.py
from __future__ import annotations

from typing import TypedDict

from ml.api.ollama_calls import EmbeddingModelClient, ReasoningModelClient


class ModelClients(TypedDict):
    chat: ReasoningModelClient
    embeddings: EmbeddingModelClient
