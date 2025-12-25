"""
LangGraph state machine for RAG system
"""
from langgraph.graph import StateGraph, END
from langgraph.types import CachePolicy
from langgraph.cache.memory import InMemoryCache
from agents.state import AgentState
from agents.nodes.router import route_query, route_decision
from agents.nodes.rag import rag_retrieve
from agents.nodes.tools import call_tools
from agents.nodes.generator import generate_answer
from observability.langfuse_client import LangFuseClient
from config.settings import settings
from services.redis_checkpointer import get_checkpointer

import time
import hashlib
import json

# Import observe decorator if LangFuse is available
try:
    from langfuse import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # Create a no-op decorator if langfuse is not available
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


def clean_state_for_caching(state: dict) -> dict:
    """
    Clean state by removing unpicklable objects before caching

    Converts:
    - deque to list (MessagesState uses deque)
    - numpy types to native Python types (from vector search/reranking)

    Args:
        state: Original state dictionary

    Returns:
        Cleaned state safe for msgpack serialization
    """
    import numpy as np

    def convert_numpy_types(obj):
        """Recursively convert numpy types to native Python types"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(convert_numpy_types(item) for item in obj)
        else:
            return obj

    cleaned = dict(state)

    # Convert deque to list (MessagesState uses deque which is not msgpack serializable)
    if "messages" in cleaned:
        from collections import deque
        if isinstance(cleaned["messages"], deque):
            cleaned["messages"] = list(cleaned["messages"])

    # Convert numpy types to native Python types (from retrieved_docs, reranked_docs, etc.)
    cleaned = convert_numpy_types(cleaned)

    return cleaned


def cache_key_for_state(state: dict) -> str:
    """
    Generate cache key from INPUT state only (before node execution)

    IMPORTANT: Cache key должен зависеть ТОЛЬКО от входных данных,
    а не от результатов выполнения нод. Иначе кэш никогда не сработает,
    так как при первом запуске результатов еще нет.

    Args:
        state: Agent state dictionary

    Returns:
        Hash string representing the input query
    """
    # Cache based on user query only
    # This ensures same question = same cache key
    user_query = state.get("user_query", "")

    # Generate hash from query
    return hashlib.sha256(user_query.encode()).hexdigest()


def make_cacheable_node(node_func):
    """
    Wrapper to clean state after node execution for caching

    Args:
        node_func: Original node function

    Returns:
        Wrapped function that cleans state
    """
    def wrapped(state):
        # Execute original node
        result = node_func(state)
        # Clean result for caching
        return clean_state_for_caching(result)
    return wrapped


def create_rag_graph() -> StateGraph:
    r"""
    Create the RAG workflow graph

    Graph structure:
        START
          ↓
        Router (classify query)
          ↓
        /   \
       /     \
      RAG   Tools (API calls)
       \     /
        \   /
         ↓
      Generator (create answer)
          ↓
         END
    """
    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes with cache policies for performance optimization
    # Wrap nodes to clean unpicklable objects before caching
    # Use custom key_func to generate cache keys from user query only

    # Router: cache routing decisions (TTL: 1 hour - routing logic stable)
    workflow.add_node(
        "router",
        make_cacheable_node(route_query) if settings.cache.enabled else route_query,
        cache_policy=CachePolicy(
            ttl=settings.cache.ttl_router,
            key_func=cache_key_for_state
        ) if settings.cache.enabled else None
    )

    # RAG: cache document search results (TTL: 30 min - docs rarely change)
    workflow.add_node(
        "rag",
        make_cacheable_node(rag_retrieve) if settings.cache.enabled else rag_retrieve,
        cache_policy=CachePolicy(
            ttl=settings.cache.ttl_rag,
            key_func=cache_key_for_state
        ) if settings.cache.enabled else None
    )

    # Tools: cache API calls (TTL: 5 min - operational data changes frequently)
    workflow.add_node(
        "tools",
        make_cacheable_node(call_tools) if settings.cache.enabled else call_tools,
        cache_policy=CachePolicy(
            ttl=settings.cache.ttl_tools,
            key_func=cache_key_for_state
        ) if settings.cache.enabled else None
    )

    # Generator: cache LLM responses (TTL: 15 min)
    workflow.add_node(
        "generator",
        make_cacheable_node(generate_answer) if settings.cache.enabled else generate_answer,
        cache_policy=CachePolicy(
            ttl=settings.cache.ttl_generator,
            key_func=cache_key_for_state
        ) if settings.cache.enabled else None
    )

    # Set entry point
    workflow.set_entry_point("router")

    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "rag": "rag",
            "tools": "tools",
            "end": END
        }
    )

    # Both RAG and Tools flow to Generator
    workflow.add_edge("rag", "generator")
    workflow.add_edge("tools", "generator")

    # Generator flows to END
    workflow.add_edge("generator", END)

    # Get checkpointer for state persistence (Redis or Memory)
    checkpointer = None
    if settings.redis.checkpoint_enabled:
        checkpointer = get_checkpointer()
        if checkpointer:
            checkpointer_type = settings.redis.checkpointer_type.upper()
            print(f"✓ Checkpointing enabled ({checkpointer_type} mode)")
        else:
            print("⚠ Checkpointing disabled (initialization failed)")

    # Initialize cache for node-level caching (performance)
    cache = None
    if settings.cache.enabled:
        cache = InMemoryCache()
        print("✓ Node caching enabled (InMemoryCache)")
        print(f"  - Router TTL: {settings.cache.ttl_router}s")
        print(f"  - RAG TTL: {settings.cache.ttl_rag}s")
        print(f"  - Tools TTL: {settings.cache.ttl_tools}s")
        print(f"  - Generator TTL: {settings.cache.ttl_generator}s")
    else:
        print("⚠ Node caching disabled")

    # Compile graph with both checkpointer (state persistence) and cache (performance)
    graph = workflow.compile(
        checkpointer=checkpointer,  # For state persistence (Redis or Memory)
        cache=cache                  # For skipping expensive node executions
    )

    return graph


# Global graph instance
_graph = None


def get_rag_graph():
    """Get or create RAG graph"""
    global _graph
    if _graph is None:
        _graph = create_rag_graph()
        print("✓ RAG graph compiled")
    return _graph


def process_query(user_query: str, user_id: str = None, session_id: str = None) -> dict:
    """
    Process a user query through the RAG graph

    Args:
        user_query: User's question
        user_id: User ID for context (defaults to demo user)
        session_id: Session ID for chat history (defaults to user_id)

    Returns:
        Dictionary with answer and sources
    """
    start_time = time.time()

    # Initialize Langfuse trace
    langfuse_client = LangFuseClient.get_client()
    trace = None
    trace_id = None
    if langfuse_client:
        trace = langfuse_client.trace(
            name="rag_query",
            user_id=user_id or settings.demo_user_id,
            session_id=session_id or f"session_{user_id or settings.demo_user_id}",
            input={"query": user_query}
        )
        # Extract trace ID for passing to nodes
        trace_id = trace.id if trace else None

    # Use demo user if not specified
    if not user_id:
        user_id = settings.demo_user_id

    # Use user_id as session_id if not specified
    if not session_id:
        session_id = f"session_{user_id}"

    # Load chat history from Redis
    from services.memory_service import get_memory_service
    memory_service = get_memory_service()
    chat_history = memory_service.get_messages_for_llm(session_id, limit=10)

    # Save user message to history
    memory_service.add_message(session_id, "user", user_query)

    # Initialize state
    initial_state = AgentState(
        user_id=user_id,
        user_query=user_query,
        session_id=session_id,
        chat_history=chat_history,
        query_type=None,
        retrieved_docs=[],
        reranked_docs=[],
        rewritten_query=None,
        tool_results=[],
        is_safe_query=True,
        guardrail_message=None,
        answer=None,
        sources=[],
        routing_reason=None,
        cache_hit=False,
        processing_time_ms=None,
        messages=[],
        langfuse_trace_id=trace_id  # Pass trace ID to nodes (serializable)
    )

    # Get graph
    graph = get_rag_graph()

    try:
        # Run graph with checkpointing support
        config = {
            "run_name": f"rag_query_{user_id}",
            "configurable": {
                "thread_id": session_id,  # Use session_id as thread_id for checkpointing
                "checkpoint_ns": ""  # Default checkpoint namespace
            }
        }

        final_state = graph.invoke(initial_state, config=config)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Extract answer
        answer = final_state.get("answer", "Sorry, I couldn't process your query.")

        # Save assistant response to history
        memory_service.add_message(
            session_id,
            "assistant",
            answer,
            metadata={
                "query_type": final_state.get("query_type"),
                "sources": final_state.get("sources", [])
            }
        )

        # Extract results
        result = {
            "answer": answer,
            "sources": final_state.get("sources", []),
            "query_type": final_state.get("query_type"),
            "routing_reason": final_state.get("routing_reason"),
            "processing_time_ms": processing_time,
            "session_id": session_id,
        }

        print(f"✓ Query processed in {processing_time:.2f}ms")

        # Update Langfuse trace with result and add quality scores
        if trace:
            try:
                trace.update(
                    output={"answer": answer, "query_type": final_state.get("query_type")},
                    metadata={
                        "processing_time_ms": processing_time,
                        "sources_count": len(final_state.get("sources", [])),
                        "routing_reason": final_state.get("routing_reason")
                    }
                )

                # Add quality scores using evaluation service
                from services.evaluation_service import get_evaluation_service
                eval_service = get_evaluation_service()

                # 1. Relevance: how well the answer addresses the query
                relevance_score = eval_service.evaluate_relevance(
                    query=user_query,
                    answer=answer
                )
                trace.score(
                    name="relevance",
                    value=relevance_score,
                    comment="LLM-as-judge evaluation of answer relevance"
                )

                # 2. Context precision: quality of retrieved documents (for documentation queries)
                if final_state.get("query_type") == "documentation" and final_state.get("retrieved_docs"):
                    precision_score, precision_comment = eval_service.evaluate_context_precision(
                        query=user_query,
                        retrieved_docs=final_state.get("retrieved_docs", [])
                    )
                    trace.score(
                        name="context_precision",
                        value=precision_score,
                        comment=precision_comment
                    )

                    # 2b. Recall: whether all necessary information was retrieved
                    recall_score, recall_comment = eval_service.evaluate_recall(
                        query=user_query,
                        answer=answer,
                        retrieved_docs=final_state.get("retrieved_docs", [])
                    )
                    trace.score(
                        name="recall",
                        value=recall_score,
                        comment=recall_comment
                    )

                # 3. Response time score (faster is better)
                latency_score = 1.0 if processing_time < 3000 else 0.7 if processing_time < 5000 else 0.5
                trace.score(
                    name="response_time",
                    value=latency_score,
                    comment=f"Response time: {processing_time:.0f}ms"
                )

                langfuse_client.flush()
            except Exception as lf_error:
                print(f"⚠ Failed to update Langfuse trace: {lf_error}")

        return result

    except Exception as e:
        print(f"✗ Error processing query: {e}")
        import traceback
        traceback.print_exc()

        # Update Langfuse trace with error
        if trace:
            try:
                trace.update(
                    output={"error": str(e)},
                    level="ERROR",
                    status_message=str(e)
                )
                langfuse_client.flush()
            except Exception as lf_error:
                print(f"⚠ Failed to update Langfuse trace: {lf_error}")

        error_result = {
            "answer": f"An error occurred while processing your query: {str(e)}",
            "sources": [],
            "query_type": "error",
            "processing_time_ms": (time.time() - start_time) * 1000,
            "session_id": session_id,  # Always return session_id
        }

        return error_result
