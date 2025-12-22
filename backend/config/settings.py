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


class LangFuseSettings(BaseModel):
    """LangFuse observability configuration"""
    public_key: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    host: str = os.getenv("LANGFUSE_HOST", "http://langfuse:3000")
    enabled: bool = bool(os.getenv("LANGFUSE_PUBLIC_KEY"))


class RAGSettings(BaseModel):
    """RAG pipeline configuration"""
    # Search settings
    top_k: int = 3
    rerank_enabled: bool = True
    rerank_top_k: int = 3

    # Query enhancement
    query_rewriting_enabled: bool = True

    # Security
    guardrails_enabled: bool = True


class AppSettings(BaseModel):
    """Main application settings"""
    # Demo user for testing (hardcoded)
    demo_user_id: str = "user_123"
    demo_user_name: str = "Demo User"

    # Component settings
    llm: LLMSettings = LLMSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    weaviate: WeaviateSettings = WeaviateSettings()
    redis: RedisSettings = RedisSettings()
    langfuse: LangFuseSettings = LangFuseSettings()
    rag: RAGSettings = RAGSettings()


# Global settings instance
settings = AppSettings()
