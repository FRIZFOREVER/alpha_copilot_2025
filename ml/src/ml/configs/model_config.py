import os
from typing import Literal, Union
from pydantic import BaseModel, Field, model_validator


_DEFAULT_BASE_URL = "http://ollama:11434/v1"

_MODEL_ENV_VARS = {
    "chat": "OLLAMA_REASONING_MODEL",
    "embeddings": "OLLAMA_EMBEDDING_MODEL",
}

def _get_model_name_from_env(kind: Literal["chat", "embeddings"]) -> str:
    return os.getenv(_MODEL_ENV_VARS[kind])

class ClientSettings(BaseModel):

    model: str = Field(
        default=None,
        description="Model name"
        )

    base_url: str = Field(
        default=_DEFAULT_BASE_URL,
        description="Ollama URL to call"
    )

    keep_alive: Union[int, str] = Field(
        default=-1, # default doesn't allow it to unload
        description=("How long till ollama unloads a model from GPU")
    )

class ReasoningModelOptions(BaseModel):
    
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Default temperature"
    )

    top_p: float = Field(
        default=0.9,
        description="Nucleus sampling cutoff"
    )

    num_ctx: int = Field(
        default=32768,
        description="Default context window size"
    )

    num_predict: int = Field(
        default=-1, # -1 stands for infinite
        description="Maximum amount of new tokens. -1 stands for unlimited"
    )

class ReasoningClientSettings(ClientSettings):

    options: ReasoningModelOptions = Field(
        default=ReasoningModelOptions(),
        description="Contains fallback params for options"
    )

    @model_validator(mode="after")
    def define_chat_model_name(self):
        if not self.model:
            self.model = _get_model_name_from_env("chat")

class EmbeddingModelOptions(BaseModel):

    num_ctx: int = Field(
        default=32768,
        description="Default max context window size"
    )

class EmbeddingClientSettings(ClientSettings):
   
    options: EmbeddingModelOptions = Field(
        default=EmbeddingModelOptions(),
        description="Contains fallback params for options"
    )

    @model_validator(mode="after")
    def define_chat_model_name(self):
        if not self.model:
            self.model = _get_model_name_from_env("embeddings")