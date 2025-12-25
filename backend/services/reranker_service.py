"""
Reranker Service - re-ranks retrieved documents using FlashRank or Cohere
"""
from typing import List, Dict, Any, Optional
from config.settings import settings
import os


class RerankerService:
    """Service for re-ranking retrieved documents"""

    def __init__(self):
        """Initialize the reranker (lazy loading)"""
        print("[RerankerService] __init__ called - creating new instance")
        self._ranker = None
        self._RerankRequest = None
        self._initialized = False
        self._reranker_type = settings.rag.reranker_type

    def _ensure_ranker(self):
        """Lazy initialization of the ranker"""
        if self._initialized:
            return

        self._initialized = True

        if not settings.rag.rerank_enabled:
            print("[RerankerService] Reranking is disabled in settings")
            return

        if self._reranker_type == "cohere":
            self._init_cohere_ranker()
        elif self._reranker_type == "flashrank":
            self._init_flashrank_ranker()
        else:
            print(f"⚠ Unknown reranker type: {self._reranker_type}, using FlashRank")
            self._init_flashrank_ranker()

    def _init_cohere_ranker(self):
        """Initialize Cohere reranker"""
        try:
            import cohere

            api_key = settings.rag.cohere_api_key
            if not api_key:
                print("⚠ COHERE_API_KEY not set, falling back to FlashRank")
                self._init_flashrank_ranker()
                return

            self._ranker = cohere.Client(api_key)
            print(f"✓ Cohere reranker initialized with model: {settings.rag.cohere_rerank_model}")
        except ImportError as e:
            print(f"⚠ Cohere not available, falling back to FlashRank: {e}")
            self._init_flashrank_ranker()
        except Exception as e:
            print(f"✗ Failed to initialize Cohere: {e}")
            self._ranker = None

    def _init_flashrank_ranker(self):
        """Initialize FlashRank reranker"""
        try:
            from flashrank import Ranker, RerankRequest

            # Use persistent cache directory
            cache_dir = os.getenv("FLASHRANK_CACHE_DIR", "/app/.cache/flashrank")
            os.makedirs(cache_dir, exist_ok=True)

            print(f"[RerankerService] Initializing FlashRank Ranker with cache_dir={cache_dir}")
            self._ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=cache_dir)
            self._RerankRequest = RerankRequest
            self._reranker_type = "flashrank"
            print("✓ FlashRank reranker initialized")
        except ImportError as e:
            print(f"⚠ FlashRank not available, reranking disabled: {e}")
            self._ranker = None
        except Exception as e:
            print(f"✗ Failed to initialize FlashRank: {e}")
            self._ranker = None

    @property
    def ranker(self):
        """Get ranker instance (with lazy initialization)"""
        self._ensure_ranker()
        return self._ranker

    @property
    def RerankRequest(self):
        """Get RerankRequest class (with lazy initialization)"""
        self._ensure_ranker()
        return self._RerankRequest

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on relevance to the query

        Args:
            query: User query
            documents: List of documents from vector search
            top_k: Number of top documents to return (default: settings.rag.final_top_k)

        Returns:
            List of re-ranked documents
        """
        if not self.ranker or not documents:
            return documents[:top_k] if top_k else documents

        if top_k is None:
            top_k = settings.rag.final_top_k

        try:
            if self._reranker_type == "cohere":
                return self._rerank_cohere(query, documents, top_k)
            else:
                return self._rerank_flashrank(query, documents, top_k)

        except Exception as e:
            print(f"✗ Reranking failed, returning original documents: {e}")
            return documents[:top_k]

    def _rerank_cohere(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Re-rank documents using Cohere"""
        # Prepare documents for Cohere
        doc_texts = [doc.get("content", "") for doc in documents]

        # Perform reranking
        response = self.ranker.rerank(
            query=query,
            documents=doc_texts,
            top_n=top_k,
            model=settings.rag.cohere_rerank_model
        )

        # Map results back to original documents
        reranked_docs = []
        for result in response.results:
            original_doc = documents[result.index]
            reranked_doc = original_doc.copy()
            reranked_doc["rerank_score"] = result.relevance_score
            reranked_docs.append(reranked_doc)

        print(f"[Reranker:Cohere] Re-ranked {len(documents)} → {len(reranked_docs)} documents")

        return reranked_docs

    def _rerank_flashrank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Re-rank documents using FlashRank"""
        # Prepare documents for FlashRank
        passages = []
        for idx, doc in enumerate(documents):
            passages.append({
                "id": idx,
                "text": doc.get("content", ""),
                "meta": {
                    "title": doc.get("title", ""),
                    "filename": doc.get("filename", ""),
                    "chunk_id": doc.get("chunk_id", 0),
                    "distance": doc.get("distance")
                }
            })

        # Create rerank request
        rerank_request = self.RerankRequest(query=query, passages=passages)

        # Perform reranking
        results = self.ranker.rerank(rerank_request)

        # Sort by score and take top_k
        reranked_docs = []
        for result in results[:top_k]:
            original_doc = documents[result["id"]]
            # Add rerank score to the document
            reranked_doc = original_doc.copy()
            reranked_doc["rerank_score"] = result["score"]
            reranked_docs.append(reranked_doc)

        print(f"[Reranker:FlashRank] Re-ranked {len(documents)} → {len(reranked_docs)} documents")

        return reranked_docs


# Global instance
_reranker_service: Optional[RerankerService] = None


def get_reranker_service() -> RerankerService:
    """Get or create the global reranker service instance"""
    global _reranker_service
    if _reranker_service is None:
        _reranker_service = RerankerService()
    return _reranker_service
