from .voice_validation_prompt import get_voice_validation_prompt, VoiceValidationResponse
from .fast_answer_prompt import get_fast_answer_prompt

__all__ = [
    "get_voice_validation_prompt", "VoiceValidationResponse", # Voice validation
    "get_fast_answer_prompt" # Fast answer prompting
]