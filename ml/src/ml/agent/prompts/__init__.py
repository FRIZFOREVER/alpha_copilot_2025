from .fast_answer_prompt import get_fast_answer_prompt
from .tag_define_prompt import get_tag_define_prompt
from .voice_validation_prompt import (
    VoiceValidationResponse,
    get_voice_validation_prompt,
)

__all__ = [
    "get_voice_validation_prompt",
    "VoiceValidationResponse",  # Voice validation
    "get_fast_answer_prompt",  # Fast answer prompting
    "get_tag_define_prompt",
]

