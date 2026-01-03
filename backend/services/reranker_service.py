"""
Reranker Service - re-ranks retrieved documents using FlashRank or Cohere
Clean service - no env reading, all configuration passed via constructor
"""
from typing import List, Dict, Any, Optional
import os


class RerankerService:
    """Service for re-ranking retrieved documents"""

    def __init__(
        self,
        reranker_type: str = "flashrank",
        rerank_enabled: bool = True,
        cohere_api_key: Optional[str] = None,
        cohere_rerank_model: str = "rerank-english-v3.0",
        flashrank_cache_dir: str = "/app/.cache/flashrank",
        final_top_k: int = 7
    ):
        """
        Initialize the reranker service

        Args:
            reranker_type: Type of reranker ("flashrank" or "cohere")
            rerank_enabled: Whether reranking is enabled
            cohere_api_key: Cohere API key (required if reranker_type="cohere")
            cohere_rerank_model: Cohere rerank model name
            flashrank_cache_dir: Cache directory for FlashRank models
            final_top_k: Default number of documents to return after reranking
        """
        self._reranker_type = reranker_type
        self._rerank_enabled = rerank_enabled
        self._cohere_api_key = cohere_api_key
        self._cohere_rerank_model = cohere_rerank_model
        self._flashrank_cache_dir = flashrank_cache_dir
        self._final_top_k = final_top_k

        self._ranker = None
        self._RerankRequest = None
        self._initialized = False

    def _ensure_ranker(self):
        """Lazy initialization of the ranker"""
        if self._initialized:
            return

        self._initialized = True

        if not self._rerank_enabled:
            print("[RerankerService] Reranking is disabled")
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

            if not self._cohere_api_key:
                print("⚠ COHERE_API_KEY not set, falling back to FlashRank")
                self._init_flashrank_ranker()
                return

            self._ranker = cohere.Client(self._cohere_api_key)
            print(f"✓ Cohere reranker initialized with model: {self._cohere_rerank_model}")
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

            # Create cache directory
            os.makedirs(self._flashrank_cache_dir, exist_ok=True)

            print(f"[RerankerService] Initializing FlashRank with cache_dir={self._flashrank_cache_dir}")
            self._ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=self._flashrank_cache_dir)
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
            top_k: Number of top documents to return (default: final_top_k from constructor)

        Returns:
            List of re-ranked documents
        """
        if not self.ranker or not documents:
            return documents[:top_k] if top_k else documents

        if top_k is None:
            top_k = self._final_top_k

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
            model=self._cohere_rerank_model
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
