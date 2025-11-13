from typing import Iterator, Optional
from ml.api.ollama_calls import ReasoningModelClient
from ollama import ChatResponse
from pydantic import BaseModel
from ml.agent.prompts import get_voice_validation_prompt, VoiceValidationResponse
from ml.configs.message import ChatHistory, Message

class StreamChunk(BaseModel):
    model: str
    created_at: str = None
    done: bool = False
    done_reason: Optional[str] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    message: Message = None

def validate_voice(voice_decoding: Message, reasoning_client: ReasoningModelClient) -> bool:
    prompt: ChatHistory
    schema: type[VoiceValidationResponse]

    prompt, schema = get_voice_validation_prompt(voice_decoding)
    
    return reasoning_client.call_structured(
        prompt,
        schema,
        options={
            "temperature": 0.0
        }
    ).voice_is_valid

def form_final_report(reasoning_client: ReasoningModelClient) -> Iterator[ChatResponse]:
    message: str = "Извините, мне не удалось распознать вашу просьбу\nПопробуйте ещё раз или напишите текстом"

    for _, char in enumerate(message):
        # Каждое сообщение содержит только текущий символ
        chunk = StreamChunk(
            model=reasoning_client.settings.model,
            done=False,
            # Возможно здесь насрано
            message=Message(
                role="assistant",
                content=char,
            ),
        )
        yield chunk