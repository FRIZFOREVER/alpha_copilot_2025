# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingTypeArgument=false

from langgraph.graph import StateGraph

from ml.domain.models import GraphState
from ml.domain.workflow.agent.nodes import define_mode, validate_tag, validate_voice


def create_pipeline() -> StateGraph:
    # Builder
    workflow: StateGraph = StateGraph(GraphState)

    # general route
    workflow.add_node("Voice validadtion", validate_voice)
    workflow.add_node("Tag validadtion", validate_tag)
    workflow.add_node("Mode definition", define_mode)

    workflow.add_edge("Voice validadtion", "Tag validadtion")
    workflow.add_edge("Tag validadtion", "Mode definition")

    # entrypoint
    workflow.set_entry_point("Voice validadtion")

    # compile
    app: StateGraph = workflow.compile()  # type: ignore[reportUnknownMemberType]

    return app
