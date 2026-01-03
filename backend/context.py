"""
Application Context - Composition Root
All dependencies are created and wired here
"""
from typing import Optional
from config.settings import AppSettings
from infra.weaviate_client import WeaviateClient
from infra.llm_client import create_llm_client
from services.reranker_service import RerankerService
from services.memory_service import MemoryService
from services.rag_service import RAGService
import os


class AppContext:
    """
    Application context - composition root for dependency injection
    Creates and manages all application dependencies
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        """
        Initialize application context

        Args:
            settings: Application settings (creates new if not provided)
        """
        # Settings (singleton)
        self.settings = settings or AppSettings()

        # Infrastructure layer (singletons)
        self.weaviate_client: Optional[WeaviateClient] = None
        self.llm_client = None

        # Service layer (singletons)
        self.reranker_service: Optional[RerankerService] = None
        self.memory_service: Optional[MemoryService] = None
        self.rag_service: Optional[RAGService] = None

        # Graph will be created in agents/graph.py
        self.rag_graph = None

    def startup(self) -> None:
        """
        Initialize all resources on app startup
        Eager initialization - all errors will be caught at startup
        """
        print("🚀 Initializing AppContext...")

        try:
            # 1. Infrastructure layer
            self._init_infrastructure()

            # 2. Service layer
            self._init_services()

            # 3. Graph layer (imported here to avoid circular dependency)
            from agents.graph import create_rag_graph
            self.rag_graph = create_rag_graph(
                settings=self.settings,
                rag_service=self.rag_service,
                memory_service=self.memory_service
            )

            print("✅ AppContext initialized successfully")

        except Exception as e:
            print(f"❌ Failed to initialize AppContext: {e}")
            raise

    def _init_infrastructure(self) -> None:
        """Initialize infrastructure components"""
        print("📦 Initializing infrastructure...")

        # Weaviate client
        self.weaviate_client = WeaviateClient(
            url=self.settings.weaviate.url,
            collection_name=self.settings.weaviate.collection_name
        )
        self.weaviate_client.connect()

        # LLM client
        self.llm_client = create_llm_client(self.settings.llm)

    def _init_services(self) -> None:
        """Initialize service layer"""
        print("🔧 Initializing services...")

        # Reranker service
        flashrank_cache_dir = os.getenv("FLASHRANK_CACHE_DIR", "/app/.cache/flashrank")
        self.reranker_service = RerankerService(
            reranker_type=self.settings.rag.reranker_type,
            rerank_enabled=self.settings.rag.rerank_enabled,
            cohere_api_key=self.settings.rag.cohere_api_key,
            cohere_rerank_model=self.settings.rag.cohere_rerank_model,
            flashrank_cache_dir=flashrank_cache_dir,
            final_top_k=self.settings.rag.final_top_k
        )

        # Memory service
        self.memory_service = MemoryService(
            redis_url=self.settings.redis.url,
            memory_type=self.settings.redis.memory_type
        )

        # RAG service
        self.rag_service = RAGService(
            llm_client=self.llm_client,
            weaviate_client=self.weaviate_client,
            reranker=self.reranker_service,
            embedding_model=self.settings.embedding.model,
            search_method=self.settings.rag.search_method,
            hybrid_alpha=self.settings.rag.hybrid_alpha,
            initial_top_k=self.settings.rag.initial_top_k,
            final_top_k=self.settings.rag.final_top_k,
            rerank_enabled=self.settings.rag.rerank_enabled
        )

    def shutdown(self) -> None:
        """
        Cleanup all resources on app shutdown
        """
        print("🛑 Shutting down AppContext...")

        try:
            # Close Weaviate connection
            if self.weaviate_client:
                self.weaviate_client.close()

            print("✅ AppContext shut down successfully")

        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")
