from typing import List
from pydantic import BaseModel
from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Role, Message
from ml.agent.prompts.research_prompt import PROMPT as RESEARCH_PROMPT
from ml.agent.prompts.analysis_prompt import PROMPT as ANALYSIS_PROMPT
from ml.agent.prompts.synthesis_prompt import PROMPT as SYNTHESIS_PROMPT
from ml.agent.graph.nodes.evidence import format_evidence_context


class SearchQueries(BaseModel):
    """Structured output for search queries."""
    queries: List[str]


class AnalysisResult(BaseModel):
    """Structured output for analysis."""
    sufficient: bool
    needs_more_research: bool
    analysis: str
    missing_info: str = ""


def research_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Generate search queries for research."""

    state.record_event(
        "node.enter",
        node="research",
        iteration=state.research_iteration,
    )

    # Get user message
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

    state.record_event(
        "research.input",
        node="research",
        user_message_preview=preview,
    )

    if not user_message:
        state.needs_more_research = False
        state.record_event(
            "research.no_user_message",
            node="research",
        )
        return state
    
    # Add search history context
    context = RESEARCH_PROMPT
    if state.search_history:
        context += f"\n\nПредыдущие поиски:\n"
        for search in state.search_history[-3:]:  # Last 3 searches
            context += f"- {search.get('query', '')}\n"
    
    # Prepare messages
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_message}
    ]
    
    # Get search queries
    try:
        queries_output: SearchQueries = client.call_structured(
            messages=messages,
            output_schema=SearchQueries
        )

        # Store queries for tool execution
        state.tool_results = [
            {"type": "search_query", "query": q} for q in queries_output.queries
        ]
        state.record_event(
            "research.queries_generated",
            node="research",
            queries=queries_output.queries,
        )
    except Exception as e:
        # Fallback: use user message as query
        state.tool_results = [
            {"type": "search_query", "query": user_message}
        ]
        state.record_event(
            "research.error",
            node="research",
            error=str(e),
            fallback_query=user_message,
        )

    return state


def analyze_results_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Analyze search results and decide if more research is needed."""

    state.record_event(
        "node.enter",
        node="analyze",
        evidence_count=len(state.evidence),
    )

    # Get user message
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

    state.record_event(
        "analyze.input",
        node="analyze",
        user_message_preview=preview,
    )

    if not user_message:
        state.needs_more_research = False
        state.record_event(
            "analyze.no_user_message",
            node="analyze",
        )
        return state
    
    # Prepare search results context
    results_context = format_evidence_context(state)
    
    # Prepare messages
    messages = [
        {"role": "system", "content": ANALYSIS_PROMPT},
        {"role": "user", "content": f"Запрос пользователя: {user_message}\n\n{results_context}"}
    ]
    
    # Get analysis
    try:
        analysis: AnalysisResult = client.call_structured(
            messages=messages,
            output_schema=AnalysisResult
        )

        state.needs_more_research = (
            analysis.needs_more_research
            and not analysis.sufficient
            and state.research_iteration < state.max_research_iterations
        )
        analysis_summary = analysis.analysis[:500]
        if len(analysis.analysis) > 500:
            analysis_summary += "…"
        state.record_event(
            "analyze.result",
            node="analyze",
            sufficient=analysis.sufficient,
            needs_more_research=analysis.needs_more_research,
            missing_info=analysis.missing_info,
            analysis_summary=analysis_summary,
        )
    except Exception as e:
        # Default: don't need more research if we have some results
        state.needs_more_research = (
            len(state.tool_results) == 0
            and state.research_iteration < state.max_research_iterations
        )
        state.record_event(
            "analyze.error",
            node="analyze",
            error=str(e),
            fallback_needs_more_research=state.needs_more_research,
        )

    return state


def synthesize_answer_node(state: GraphState, _client: _ReasoningModelClient) -> GraphState:
    """Prepare synthesis prompt from search results."""

    state.record_event(
        "node.enter",
        node="synthesize",
        evidence_count=len(state.evidence),
    )

    # Get user message
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

    state.record_event(
        "synthesize.input",
        node="synthesize",
        user_message_preview=preview,
    )

    if not user_message:
        state.final_answer = "Извините, не удалось найти запрос пользователя."
        state.stream_messages = []
        state.final_prompt_messages = []
        state.record_event(
            "synthesize.no_user_message",
            node="synthesize",
        )
        return state
    
    # Prepare search results context
    results_context = format_evidence_context(state)
    
    # Prepare messages
    messages = [
        {"role": "system", "content": SYNTHESIS_PROMPT},
        {"role": "user", "content": f"Запрос пользователя: {user_message}\n\n{results_context}"}
    ]

    state.final_prompt_messages = messages
    state.stream_messages = messages
    state.final_answer = None

    state.record_event(
        "synthesize.prompt_prepared",
        node="synthesize",
        message_count=len(messages),
    )

    return state
