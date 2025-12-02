# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingTypeArgument=false

from langgraph.graph import END, StateGraph

from ml.domain.models import GraphState
from ml.domain.workflow.agent.conditionals import mode_decision, research_decision
from ml.domain.workflow.agent.nodes import (
    define_mode,
    fast_answer,
    final_stream,
    flash_memories,
    research_answer,
    research_observer,
    research_reason,
    research_tool_call,
    validate_tag,
    validate_voice,
)


def create_pipeline() -> StateGraph:
    # Builder
    workflow: StateGraph = StateGraph(GraphState)

    # general route
    # TODO: Add conditional validation jump node
    workflow.add_node("Voice validadtion", validate_voice)
    workflow.add_node("Tag validadtion", validate_tag)
    workflow.add_node("Mode definition", define_mode)
    workflow.add_node("Final node", final_stream)

    workflow.add_edge("Voice validadtion", "Tag validadtion")
    workflow.add_edge("Tag validadtion", "Mode definition")
    workflow.add_conditional_edges(
        "Mode definition",
        mode_decision,
        {
            "fast_pipeline": "Flash memories",
            "thinking_pipeline": "Thinking pipeline",  # TODO: Wire pipeline
            "research_pipeline": "Research reason",
        },
    )

    # Fast
    workflow.add_node("Flash memories", flash_memories)  # TODO: Implement memories
    workflow.add_node("Fast answer", fast_answer)

    workflow.add_edge("Flash memories", "Fast answer")
    workflow.add_edge("Fast answer", "Final node")

    # Thinking
    # TODO: add thinking workflow
    workflow.add_node(...)

    # Research
    workflow.add_node("Research reason", research_reason)
    workflow.add_node("Research tool call", research_tool_call)
    workflow.add_node("Research observer", research_observer)
    workflow.add_node("Research answer", research_answer)

    workflow.add_conditional_edges(
        "Research reason",
        research_decision,
        {
            "tool_call": "Research tool call",
            "finalize": "Research answer",
        },
    )

    workflow.add_edge("Research tool call", "Research observer")
    workflow.add_edge("Research observer", "Research reason")
    workflow.add_edge("Research answer", "Final node")

    # entrypoint
    workflow.set_entry_point("Voice validadtion")

    # exit point
    workflow.add_edge("Final node", END)

    # compile
    app: StateGraph = workflow.compile()  # type: ignore[reportUnknownMemberType]

    return app
