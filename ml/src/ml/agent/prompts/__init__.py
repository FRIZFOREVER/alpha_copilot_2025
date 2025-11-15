from .fast_answer_prompt import compose_fast_final_prompt
from .mode_decision_prompt import ModeDecisionResponse, get_mode_decision_prompt
from .research_answer_prompt import get_research_answer_prompt
from .research_observation_prompt import get_research_observation_prompt
from .research_reason_prompt import get_research_reason_prompt
from .research_tool_prompt import get_research_tool_prompt
from .tag_define_prompt import get_tag_define_prompt
from .thinking_answer_prompt import get_thinking_answer_prompt
from .thinking_planner_prompt import (
    PlannerToolCall,
    ThinkingPlannerStructuredOutput,
    get_thinking_planner_prompt,
)
from .voice_validation_prompt import (
    VoiceValidationResponse,
    get_voice_validation_prompt,
)

__all__: list[str] = [
    "get_voice_validation_prompt",
    "VoiceValidationResponse",  # Voice validation
    "compose_fast_final_prompt",  # Fast answer prompting
    "get_research_reason_prompt",  # Research reasoning stage
    "get_research_tool_prompt",  # Research tool selection stage
    "get_research_observation_prompt",  # Research observation synthesis
    "get_research_answer_prompt",  # Research answer assembly
    "get_tag_define_prompt",
    "get_thinking_planner_prompt",  # Thinking planner stage
    "ThinkingPlannerStructuredOutput",
    "PlannerToolCall",
    "get_thinking_answer_prompt",  # Thinking answer stage
    "get_mode_decision_prompt",  # Mode selection helper
    "ModeDecisionResponse",
]
