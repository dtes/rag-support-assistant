"""
Configuration settings for the RAG system
"""
import os
from typing import Optional
from pydantic import BaseModel


class LLMSettings(BaseModel):
    """LLM configuration"""
    provider: str = os.getenv("LLM_PROVIDER", "azure-openai")
    azure_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_BASE_URL")
    azure_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_api_version: Optional[str] = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_deployment: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://ollama:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    temperature: float = 0.7
    max_tokens: int = 1000


class EmbeddingSettings(BaseModel):
    """Embedding model configuration"""
    model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class ChunkingSettings(BaseModel):
    """Chunking configuration"""
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))


class WeaviateSettings(BaseModel):
    """Weaviate vector database configuration"""
    url: str = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
    collection_name: str = "Documentation"


class RedisSettings(BaseModel):
    """Redis cache configuration"""
    url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    # Cache TTL settings (in seconds)
    ttl_transactions: int = 60  # 1 minute for transactions
    ttl_reports: int = 300  # 5 minutes for reports
    ttl_dictionaries: int = 3600  # 1 hour for reference data
    ttl_checkpoints: int = 3600  # 1 hour for LangGraph checkpoints
    checkpoint_enabled: bool = os.getenv("CHECKPOINT_ENABLED", "true").lower() == "true"
    # Checkpointer type: "redis" or "memory"
    checkpointer_type: str = os.getenv("CHECKPOINTER_TYPE", "memory")
    # Memory service type: "redis" or "memory"
    memory_type: str = os.getenv("MEMORY_TYPE", "memory")


class LangFuseSettings(BaseModel):
    """LangFuse observability configuration"""
    public_key: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    host: str = os.getenv("LANGFUSE_HOST", "http://langfuse:3000")
    enabled: bool = bool(os.getenv("LANGFUSE_PUBLIC_KEY"))


class RAGSettings(BaseModel):
    """RAG pipeline configuration"""
    # Search settings
    search_method: str = os.getenv("SEARCH_METHOD", "vector")  # Options: "vector", "bm25", "hybrid"
    top_k: int = 3  # Legacy: used when reranking is disabled
    initial_top_k: int = int(os.getenv("RAG_INITIAL_TOP_K", "15"))  # Initial retrieval for reranking
    final_top_k: int = int(os.getenv("RAG_FINAL_TOP_K", "7"))  # Final docs after reranking
    rerank_enabled: bool = os.getenv("RERANK_ENABLED", "true").lower() == "true"
    rerank_top_k: int = 3  # Deprecated, use final_top_k instead

    # Reranker settings
    reranker_type: str = os.getenv("RERANKER_TYPE", "flashrank")  # Options: "flashrank", "cohere"
    cohere_api_key: Optional[str] = os.getenv("COHERE_API_KEY")
    cohere_rerank_model: str = os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.0")

    # Hybrid search settings
    hybrid_alpha: float = float(os.getenv("HYBRID_ALPHA", "0.5"))  # Weight for vector vs BM25 (0.5 = equal weight)

    # Query enhancement
    query_rewriting_enabled: bool = True

    # Security
    guardrails_enabled: bool = True


class CacheSettings(BaseModel):
    """Node-level caching configuration"""
    enabled: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    # TTL settings for different node types (in seconds)
    ttl_router: int = 3600    # 1 hour - routing logic rarely changes
    ttl_rag: int = 1800       # 30 minutes - documents don't update often
    ttl_tools: int = 300      # 5 minutes - operational data changes frequently
    ttl_generator: int = 900  # 15 minutes - generated answers


class AppSettings(BaseModel):
    """Main application settings"""
    # Demo user for testing (hardcoded)
    demo_user_id: str = "user_123"
    demo_user_name: str = "Demo User"

    # Component settings
    llm: LLMSettings = LLMSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    chunking: ChunkingSettings = ChunkingSettings()
    weaviate: WeaviateSettings = WeaviateSettings()
    redis: RedisSettings = RedisSettings()
    langfuse: LangFuseSettings = LangFuseSettings()
    rag: RAGSettings = RAGSettings()
    cache: CacheSettings = CacheSettings()


# Global settings instance
settings = AppSettings()
