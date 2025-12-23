"""
RAG node - retrieves and processes documentation
"""
from agents.state import AgentState
from rag_service import RAGService
from config.settings import settings

# Import observe decorator
try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


# Global RAG service instance
_rag_service: RAGService = None


def get_rag_service() -> RAGService:
    """Get or create RAG service"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def rag_retrieve(state: AgentState) -> AgentState:
    """
    RAG node: Search vector database for relevant documents

    Updates state with retrieved_docs
    """
    query = state.get("rewritten_query") or state["user_query"]

    print(f"[RAG] Searching for: {query}")

    rag_service = get_rag_service()

    # Search documents
    docs = rag_service.search_documents(query, top_k=settings.rag.top_k)

    state["retrieved_docs"] = docs

    print(f"[RAG] Retrieved {len(docs)} documents")

    # Format sources
    sources = []
    for doc in docs:
        sources.append({
            "title": doc.get("title", ""),
            "filename": doc.get("filename", "")
        })

    # Remove duplicates
    unique_sources = []
    seen = set()
    for source in sources:
        key = (source["title"], source["filename"])
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    state["sources"] = unique_sources

    return state
