"""
LangGraph state machine for RAG system
"""
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.router import route_query, route_decision
from agents.nodes.rag import rag_retrieve
from agents.nodes.tools import call_tools
from agents.nodes.generator import generate_answer
from observability.langfuse_client import LangFuseClient
from config.settings import settings
import time

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


def create_rag_graph() -> StateGraph:
    """
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

    # Add nodes
    workflow.add_node("router", route_query)
    workflow.add_node("rag", rag_retrieve)
    workflow.add_node("tools", call_tools)
    workflow.add_node("generator", generate_answer)

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

    # Compile graph
    graph = workflow.compile()

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


#@observe(name="rag_query", as_type="chain")
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
        messages=[]
    )

    # Get graph
    graph = get_rag_graph()

    try:
        # Run graph
        config = {
            "run_name": f"rag_query_{user_id}",
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

        return result

    except Exception as e:
        print(f"✗ Error processing query: {e}")
        import traceback
        traceback.print_exc()

        error_result = {
            "answer": f"An error occurred while processing your query: {str(e)}",
            "sources": [],
            "query_type": "error",
            "processing_time_ms": (time.time() - start_time) * 1000,
        }

        return error_result
