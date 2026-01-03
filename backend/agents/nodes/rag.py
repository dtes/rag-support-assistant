"""
RAG node - retrieves and processes documentation
Clean node - dependencies injected via factory function
"""
from agents.state import AgentState

# Import observe decorator
try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


def create_rag_retrieve_node(rag_service):
    """
    Factory function to create rag_retrieve node with injected dependencies

    Args:
        rag_service: RAGService instance

    Returns:
        rag_retrieve node function
    """
    def rag_retrieve(state: AgentState) -> AgentState:
        """
        RAG node: Search vector database for relevant documents

        Updates state with retrieved_docs and reranked_docs
        """
        query = state.get("rewritten_query") or state["user_query"]

        print(f"[RAG] Searching for: {query}")

        # Search documents (with reranking if enabled)
        docs = rag_service.search_documents(query, top_k=rag_service.final_top_k)

        # Store both retrieved and reranked docs
        # If reranking is enabled, docs will already be reranked
        state["retrieved_docs"] = docs
        state["reranked_docs"] = docs if rag_service.rerank_enabled else []

        print(f"[RAG] Retrieved {len(docs)} documents (reranking={'enabled' if rag_service.rerank_enabled else 'disabled'})")

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

    return rag_retrieve
