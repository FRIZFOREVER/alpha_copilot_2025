import logging

from ml.domain.models import GraphState, ModelMode
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool

logger = logging.getLogger(__name__)


def mode_decision(state: GraphState) -> str:
    mode = state.model_mode

    if mode == ModelMode.Fast:
        return "fast_pipeline"
    if mode == ModelMode.Thiking:
        return "thinking_pipeline"
    if mode == ModelMode.Research:
        return "research_pipeline"

    msg = "Failed to branch into pipeline"
    logger.error(msg)
    raise RuntimeError(msg)


def research_decision(state: GraphState) -> str:
    tool_name = state.last_executed_tool
    if tool_name is None and state.pending_tool_call is not None:
        tool_name = state.pending_tool_call.tool_name

    if tool_name is None:
        raise RuntimeError("No tool execution data available for research decision")

    if tool_name == FinalAnswerTool().name:
        return "finalize"

    return "tool_call"
