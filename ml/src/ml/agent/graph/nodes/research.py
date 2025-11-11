from typing import Dict, Any, List
from pydantic import BaseModel
from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Role, Message
from ml.agent.tools.registry import get_tool_registry
from ml.agent.prompts.research_prompt import PROMPT as RESEARCH_PROMPT
from ml.agent.prompts.analysis_prompt import PROMPT as ANALYSIS_PROMPT
from ml.agent.prompts.synthesis_prompt import PROMPT as SYNTHESIS_PROMPT


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
    
    # Get user message
    user_message = None
    for msg in reversed(state.messages):
        if msg.role == Role.user:
            user_message = msg.content
            break
    
    if not user_message:
        state.needs_more_research = False
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
    except Exception as e:
        # Fallback: use user message as query
        state.tool_results = [
            {"type": "search_query", "query": user_message}
        ]
    
    return state


def analyze_results_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Analyze search results and decide if more research is needed."""
    
    # Get user message
    user_message = None
    for msg in reversed(state.messages):
        if msg.role == Role.user:
            user_message = msg.content
            break
    
    if not user_message:
        state.needs_more_research = False
        return state
    
    # Prepare search results context
    results_context = "Результаты поиска:\n\n"
    for result in state.tool_results:
        if result.get("type") == "search_result":
            search_data = result.get("data", {})
            query = search_data.get("query", "")
            results = search_data.get("results", [])
            results_context += f"Запрос: {query}\n"
            for i, res in enumerate(results[:3], 1):  # Top 3 results per query
                excerpt = res.get("excerpt") or res.get("snippet", "")
                preview = res.get("content", "")
                results_context += f"{i}. {res.get('title', '')}\n"
                if excerpt:
                    results_context += f"   {excerpt}\n"
                if preview:
                    short_preview = preview[:300].rstrip()
                    if len(preview) > 300:
                        short_preview += "..."
                    results_context += f"   [Контент] {short_preview}\n"
            results_context += "\n"
    
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
    except Exception as e:
        # Default: don't need more research if we have some results
        state.needs_more_research = (
            len(state.tool_results) == 0 
            and state.research_iteration < state.max_research_iterations
        )
    
    return state


def synthesize_answer_node(state: GraphState, _client: _ReasoningModelClient) -> GraphState:
    """Prepare synthesis prompt from search results."""
    
    # Get user message
    user_message = None
    for msg in reversed(state.messages):
        if msg.role == Role.user:
            user_message = msg.content
            break
    
    if not user_message:
        state.final_answer = "Извините, не удалось найти запрос пользователя."
        state.stream_messages = []
        state.final_prompt_messages = []
        return state
    
    # Prepare search results context
    results_context = "Результаты поиска:\n\n"
    for result in state.tool_results:
        if result.get("type") == "search_result" and result.get("success"):
            search_data = result.get("data", {})
            query = search_data.get("query", "")
            results = search_data.get("results", [])
            results_context += f"Запрос: {query}\n"
            for i, res in enumerate(results, 1):
                excerpt = res.get("excerpt") or res.get("snippet", "")
                preview = res.get("content", "")
                results_context += f"{i}. {res.get('title', '')}\n"
                results_context += f"   URL: {res.get('url', '')}\n"
                if excerpt:
                    results_context += f"   {excerpt}\n"
                if preview:
                    short_preview = preview[:300].rstrip()
                    if len(preview) > 300:
                        short_preview += "..."
                    results_context += f"   [Контент] {short_preview}\n"
                results_context += "\n"
    
    # Prepare messages
    messages = [
        {"role": "system", "content": SYNTHESIS_PROMPT},
        {"role": "user", "content": f"Запрос пользователя: {user_message}\n\n{results_context}"}
    ]

    state.final_prompt_messages = messages
    state.stream_messages = messages
    state.final_answer = None

    return state
