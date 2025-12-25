"""
Agent state schema for LangGraph
"""
from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    State schema for the RAG agent

    Inherits from MessagesState which provides:
    - messages: List of chat messages

    Additional fields for RAG pipeline:
    """
    # User context
    user_id: str
    user_query: str
    session_id: str  # Session ID for chat history

    # Chat history
    chat_history: List[tuple]  # List of (role, content) tuples from Redis

    # Routing
    query_type: Optional[Literal["documentation", "operational", "unknown"]]  # Router decision

    # RAG pipeline
    retrieved_docs: List[Dict[str, Any]]  # Documents from vector search
    reranked_docs: List[Dict[str, Any]]  # Re-ranked documents
    rewritten_query: Optional[str]  # Enhanced query

    # Tool calling
    tool_results: List[Dict[str, Any]]  # Results from API tools

    # Security
    is_safe_query: bool  # Guardrail check passed
    guardrail_message: Optional[str]  # Message if query rejected

    # Final answer
    answer: Optional[str]
    sources: List[Dict[str, str]]

    # Metadata
    routing_reason: Optional[str]  # Why router chose this path
    cache_hit: bool  # Whether response was cached
    processing_time_ms: Optional[float]

    # Langfuse trace ID (serializable)
    langfuse_trace_id: Optional[str]  # Langfuse trace ID for logging
