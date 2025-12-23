"""
Router node - determines query type
"""
from typing import Literal
from agents.state import AgentState
from llm_client import create_llm_client

# Import observe decorator
try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


def route_query(state: AgentState) -> AgentState:
    """
    Router node: Classify query as documentation or operational

    Returns updated state with query_type and routing_reason
    """
    import time
    start_time = time.time()

    query = state["user_query"]
    trace = state.get("langfuse_trace")

    # Create span for routing step
    span = None
    if trace:
        span = trace.span(name="router", input={"query": query})

    # Create LLM client
    llm = create_llm_client()

    # System prompt for routing
    routing_prompt = f"""You are a query router for a financial SaaS system.

Your task: Classify the user's question into one of these categories:

1. "documentation" - Questions about:
   - How the system works
   - Feature explanations
   - User guides
   - General information about the service
   - Navigation help

2. "operational" - Questions requiring current data:
   - Account balances ("What's my balance?")
   - Recent transactions ("Show my expenses this month")
   - Financial reports (cash flow, profit/loss)
   - Current statistics
   - Data about categories, counterparties

User question: "{query}"

Respond in JSON format:
{{
  "query_type": "documentation" or "operational",
  "reasoning": "Brief explanation why"
}}

JSON response:"""

    try:
        # Track LLM generation with Langfuse
        generation = None
        if span:
            generation = span.generation(
                name="router_llm",
                model="gpt-4o-mini",
                input=[{"role": "system", "content": routing_prompt}]
            )

        response = llm.invoke([("system", routing_prompt)])
        content = response.content.strip()

        # Track token usage
        if generation and hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('token_usage', {})
            if usage:
                generation.end(
                    output=content,
                    usage={
                        "input": usage.get('prompt_tokens', 0),
                        "output": usage.get('completion_tokens', 0),
                        "total": usage.get('total_tokens', 0)
                    }
                )

        # Parse JSON response
        import json
        # Extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)

        state["query_type"] = result.get("query_type", "unknown")
        state["routing_reason"] = result.get("reasoning", "")

        print(f"[Router] Query type: {state['query_type']} - {state['routing_reason']}")

        # Update span with result
        if span:
            latency_ms = (time.time() - start_time) * 1000
            span.end(
                output={
                    "query_type": state["query_type"],
                    "reasoning": state["routing_reason"]
                },
                metadata={"latency_ms": latency_ms}
            )

    except Exception as e:
        print(f"[Router] Error: {e}")
        # Default to documentation on error
        state["query_type"] = "documentation"
        state["routing_reason"] = "Fallback to documentation due to routing error"

        if span:
            span.end(level="ERROR", status_message=str(e))

    return state


def route_decision(state: AgentState) -> Literal["rag", "tools", "end"]:
    """
    Conditional edge: Determine next node based on query type
    """
    if not state.get("is_safe_query", True):
        return "end"

    query_type = state.get("query_type", "unknown")

    if query_type == "documentation":
        return "rag"
    elif query_type == "operational":
        return "tools"
    else:
        # Unknown - default to RAG
        return "rag"
