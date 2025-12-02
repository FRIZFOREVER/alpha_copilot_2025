# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingTypeArgument=false

from langgraph.graph import END, StateGraph

from ml.domain.models import GraphState
from ml.domain.workflow.agent.conditionals import mode_decision
from ml.domain.workflow.agent.nodes import (
    define_mode,
    fast_answer,
    flash_memories,
    get_final_stream,
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
    workflow.add_node("Final node", get_final_stream)

    workflow.add_edge("Voice validadtion", "Tag validadtion")
    workflow.add_edge("Tag validadtion", "Mode definition")
    workflow.add_conditional_edges(
        "Mode definition",
        mode_decision,
        {
            "fast_pipeline": "Flash memories",
            "thinking_pipeline": "Thinking pipeline",  # TODO: Wire pipeline
            "research_pipeline": "Research pipeline",  # TODO: Wire here aswell
        },
    )

    # Fast
    # TODO: Add fast workflow
    workflow.add_node("Flash memories", flash_memories)
    workflow.add_node("Fast answer", fast_answer)

    # Thinking
    # TODO: add thinking workflow

    # Research
    # TODO: add research workflow

    # entrypoint
    workflow.set_entry_point("Voice validadtion")

    # exit point
    workflow.add_edge("Final node", END)

    # compile
    app: StateGraph = workflow.compile()  # type: ignore[reportUnknownMemberType]

    return app
