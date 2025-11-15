from .fast_answer_prompt import get_fast_answer_prompt
from .research_observation_prompt import get_research_observation_prompt
from .research_reason_prompt import get_research_reason_prompt
from .research_tool_prompt import get_research_tool_prompt
from .tag_define_prompt import get_tag_define_prompt
from .voice_validation_prompt import (
    VoiceValidationResponse,
    get_voice_validation_prompt,
)

__all__: list[str] = [
    "get_voice_validation_prompt",
    "VoiceValidationResponse",  # Voice validation
    "get_fast_answer_prompt",  # Fast answer prompting
    "get_research_reason_prompt",  # Research reasoning stage
    "get_research_tool_prompt",  # Research tool selection stage
    "get_research_observation_prompt",  # Research observation synthesis
    "get_tag_define_prompt",
]
