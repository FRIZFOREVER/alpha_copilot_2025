from __future__ import annotations

from typing import TypedDict

from ml.api.external.ollama_client import EmbeddingModelClient, ReasoningModelClient


class ModelClients(TypedDict):
    chat: ReasoningModelClient
    embeddings: EmbeddingModelClient
