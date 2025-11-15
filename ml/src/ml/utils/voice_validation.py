from collections.abc import Iterator

from ml.agent.prompts import VoiceValidationResponse, get_voice_validation_prompt
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory
from ml.configs.message import Message as ChatMessage
from ollama import ChatResponse
from ollama import Message as OllamaMessage
from pydantic import BaseModel


class StreamChunk(BaseModel):
    model: str
    created_at: str | None = None
    done: bool = False
    done_reason: str | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None
    message: ChatMessage | None = None


def validate_voice(voice_decoding: ChatMessage, reasoning_client: ReasoningModelClient) -> bool:
    prompt: ChatHistory
    schema: type[VoiceValidationResponse]

    prompt, schema = get_voice_validation_prompt(voice_decoding)

    return reasoning_client.call_structured(
        prompt,
        schema,
        options={
            "temperature": 0.0,
        },
    ).voice_is_valid


def form_final_report(reasoning_client: ReasoningModelClient) -> Iterator[ChatResponse]:
    fallback_message: str = (
        "Извините, мне не удалось распознать вашу просьбу\nПопробуйте ещё раз или напишите текстом"
    )

    for _, char in enumerate(fallback_message):
        response: ChatResponse = ChatResponse.model_construct(
            model=reasoning_client.settings.model,
            done=False,
            message=OllamaMessage.model_construct(
                role="assistant",
                content=char,
            ),
        )
        yield response
