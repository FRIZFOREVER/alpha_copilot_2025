from typing import Dict, Any, List
from pydantic import BaseModel
from ml.agent.graph.state import GraphState
from ml.agent.calls.model_calls import _ReasoningModelClient
from ml.configs.message import Role, Message
from ml.agent.tools.registry import get_tool_registry
import os


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
    
    # Load research prompt
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "prompts", "research_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        research_prompt = f.read()
    
    # Add search history context
    context = research_prompt
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
    
    # Load analysis prompt
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "prompts", "analysis_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        analysis_prompt = f.read()
    
    # Prepare search results context
    results_context = "Результаты поиска:\n\n"
    for result in state.tool_results:
        if result.get("type") == "search_result":
            search_data = result.get("data", {})
            query = search_data.get("query", "")
            results = search_data.get("results", [])
            results_context += f"Запрос: {query}\n"
            for i, res in enumerate(results[:3], 1):  # Top 3 results per query
                results_context += f"{i}. {res.get('title', '')}\n"
                results_context += f"   {res.get('snippet', '')}\n"
            results_context += "\n"
    
    # Prepare messages
    messages = [
        {"role": "system", "content": analysis_prompt},
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


def synthesize_answer_node(state: GraphState, client: _ReasoningModelClient) -> GraphState:
    """Synthesize final answer from search results."""
    
    # Get user message
    user_message = None
    for msg in reversed(state.messages):
        if msg.role == Role.user:
            user_message = msg.content
            break
    
    if not user_message:
        state.final_answer = "Извините, не удалось найти запрос пользователя."
        return state
    
    # Load synthesis prompt
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "prompts", "synthesis_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        synthesis_prompt = f.read()
    
    # Prepare search results context
    results_context = "Результаты поиска:\n\n"
    for result in state.tool_results:
        if result.get("type") == "search_result" and result.get("success"):
            search_data = result.get("data", {})
            query = search_data.get("query", "")
            results = search_data.get("results", [])
            results_context += f"Запрос: {query}\n"
            for i, res in enumerate(results, 1):
                results_context += f"{i}. {res.get('title', '')}\n"
                results_context += f"   URL: {res.get('url', '')}\n"
                results_context += f"   {res.get('snippet', '')}\n\n"
    
    # Prepare messages
    messages = [
        {"role": "system", "content": synthesis_prompt},
        {"role": "user", "content": f"Запрос пользователя: {user_message}\n\n{results_context}"}
    ]
    
    # Get answer
    try:
        response = client.call(messages=messages)
        state.final_answer = response.content
    except Exception as e:
        state.final_answer = f"Извините, произошла ошибка при синтезе ответа: {str(e)}"
    
    return state

