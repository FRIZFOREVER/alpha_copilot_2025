import logging
import os

import httpx
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URLS = [
    "http://ollama:11434/v1",
    "http://localhost:11434/v1",
]

MODEL_ENV_VARS = {"chat": "OLLAMA_REASONING_MODEL", "embedding": "OLLAMA_EMBEDDING_MODEL"}


class ClientSettings(BaseModel):
    """
    This is a parent model, hich is never created in a pipeline
    It's purpose is to only provide general client settings for chieldren
    """

    model: str = Field(default="", description="Model name (filled by subclasses)")

    base_url: str = Field(default="", description="Ollama URL to call")

    keep_alive: int | str = Field(
        default=-1,  # default doesn't allo it to unload
        description=("How long till ollama unloads a model from GPU"),
    )

    @field_validator("base_url", mode="before")
    @classmethod
    def define_base_url(cls, value: str | None) -> str:
        if value:
            return value

        logger.debug("Automatically defining base_url")
        for url in _DEFAULT_BASE_URLS:
            try:
                with httpx.Client(timeout=0.3) as client:
                    resp = client.get(url)
                if resp.status_code == 200:
                    # Mostly shugar. We don't really care about status code that much
                    # This doesn't gurantee that it's actually a working ollama service
                    logger.debug("Selected ollama url: %s status=%s", url, resp.status_code)
                    return url
            except httpx.RequestError:
                # In case URL is unreachable, httpx throws an error
                logger.debug("Prope error for base url %s", url)

        raise ValueError(
            "Base url is empty and no default ollama url was found\n"
            f"Tested urls: {_DEFAULT_BASE_URLS}"
        )


class ReasoningModelOptions(BaseModel):
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Default temperature")

    top_p: float = Field(default=0.9, description="Nucleus sampling cutoff")

    num_ctx: int = Field(default=32768, description="Default context window size")

    num_predict: int = Field(
        default=-1,  # -1 stands for infinite
        description="Maximum amount of new tokens. -1 stands for unlimited",
    )


class ReasoningClientSettings(ClientSettings):
    options: ReasoningModelOptions = Field(
        default=ReasoningModelOptions(), description="Contains fallback params for options"
    )

    @field_validator("model", mode="before")
    @classmethod
    def define_chat_model_name(cls, value: str | None) -> str:
        if value:
            return value

        key: str = MODEL_ENV_VARS["chat"]
        logger.debug("Automatically defining model_name")
        value = os.getenv(key)

        if value is None:
            msg = f"Environment variable {key} is required for automatic detection"
            logger.error(msg)
            raise RuntimeError(msg)

        return value


class EmbeddingModelOptions(BaseModel):
    num_ctx: int = Field(default=32768, description="Default max context window size")


class EmbeddingClientSettings(ClientSettings):
    options: EmbeddingModelOptions = Field(
        default=EmbeddingModelOptions(), description="Contains fallback params for options"
    )

    @field_validator("model", mode="before")
    @classmethod
    def define_embedding_model_name(cls, value: str | None) -> str:
        if value:
            logger.info("Embedding model name is forced: %s", value)
            return value

        key: str = MODEL_ENV_VARS["embedding"]
        logger.debug("Automatically defining embedding model name")
        value = os.getenv(key)

        if not value:
            msg = f"Environment variable {key} is required for automatic detection"
            logger.error(msg)
            raise RuntimeError(msg)

        logger.debug("Embedding model name: %s", value)
        print("Embedding model name:", value)
        return value
