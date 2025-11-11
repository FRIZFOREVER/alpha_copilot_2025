from pydantic import BaseModel
from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Role, Message
from ml.agent.prompts.planner_prompt import PROMPT as PLANNER_PROMPT
from ml.agent.graph.logging_utils import log_pipeline_event


class PlanningDecision(BaseModel):
    """Structured output for planning decision."""
    mode: str  # "research" or "fast_answer"
    reasoning: str
    requires_tools: bool


def planner_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Plan the execution mode based on user request."""

    log_pipeline_event(
        "node.enter",
        state=state,
        extra={"node": "planner", "message_count": len(state.messages)},
    )

    # Get the last user message
    user_message = None
    for msg in reversed(state.messages):
        if msg.role == Role.user:
            user_message = msg.content
            break

    if user_message:
        preview = user_message[:200]
        if len(user_message) > 200:
            preview += "…"
    else:
        preview = None

    log_pipeline_event(
        "planner.input",
        state=state,
        extra={"node": "planner", "user_message_preview": preview},
    )

    if not user_message:
        # Default to fast_answer if no user message
        state.mode = "fast_answer"
        state.planning_decision = {
            "mode": "fast_answer",
            "reasoning": "No user message found",
            "requires_tools": False
        }
        log_pipeline_event(
            "planner.decision",
            state=state,
            extra={"node": "planner", "decision": state.planning_decision},
        )
        return state
    
    # Prepare messages
    messages = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    # Get structured decision
    try:
        decision: PlanningDecision = client.call_structured(
            messages=messages,
            output_schema=PlanningDecision
        )
        
        state.mode = decision.mode
        state.planning_decision = {
            "mode": decision.mode,
            "reasoning": decision.reasoning,
            "requires_tools": decision.requires_tools
        }
        log_pipeline_event(
            "planner.decision",
            state=state,
            extra={
                "node": "planner",
                "decision": state.planning_decision,
            },
        )
    except Exception as e:
        # Fallback to fast_answer on error
        state.mode = "fast_answer"
        state.planning_decision = {
            "mode": "fast_answer",
            "reasoning": f"Error in planning: {str(e)}",
            "requires_tools": False
        }
        log_pipeline_event(
            "planner.error",
            state=state,
            extra={
                "node": "planner",
                "error": str(e),
                "decision": state.planning_decision,
            },
        )

    return state
