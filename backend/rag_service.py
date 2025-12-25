"""
RAG Service - main logic for search and answer generation
"""
import os
import weaviate
from sentence_transformers import SentenceTransformer
from llm_client import create_llm_client
from db_client import connect_weaviate
from config.settings import settings
from services.reranker_service import get_reranker_service

# Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

class RAGService:
    def __init__(self):
        """Initialize the service"""
        self.llm_client = create_llm_client()
        self.weaviate_client = connect_weaviate()
        self.reranker = get_reranker_service()

        # Load local embedding model
        if not EMBEDDING_MODEL:
            raise ValueError(
                "EMBEDDING_MODEL environment variable is not set. "
                "Please set it in your .env file (e.g., EMBEDDING_MODEL=all-MiniLM-L6-v2)"
            )

        print(f"Loading local embedding model: {EMBEDDING_MODEL}")
        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            print("✓ Local embedding model loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model '{EMBEDDING_MODEL}': {e}")

    def get_embedding(self, text: str) -> list[float]:
        """Create embedding for text using local model"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"✗ Error creating embedding: {e}")
            return None

    def _search_vector(self, documentation, query: str, limit: int):
        """Perform vector (semantic) search"""
        # Create embedding for query
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []

        print(f"Query embedding dimension: {len(query_embedding)}")

        # Vector search
        response = documentation.query.near_vector(
            near_vector=query_embedding,
            limit=limit,
            return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
        )

        # Format results
        results = []
        for item in response.objects:
            results.append({
                'content': item.properties.get('content', ''),
                'filename': item.properties.get('filename', ''),
                'title': item.properties.get('title', ''),
                'chunk_id': item.properties.get('chunk_id', 0),
                'distance': item.metadata.distance if item.metadata else None,
                'score': 1.0 - (item.metadata.distance if item.metadata else 0)  # Convert distance to similarity
            })

        return results

    def _search_bm25(self, documentation, query: str, limit: int):
        """Perform BM25 keyword search"""
        # BM25 search
        response = documentation.query.bm25(
            query=query,
            limit=limit,
            return_metadata=weaviate.classes.query.MetadataQuery(score=True)
        )

        # Format results
        results = []
        for item in response.objects:
            results.append({
                'content': item.properties.get('content', ''),
                'filename': item.properties.get('filename', ''),
                'title': item.properties.get('title', ''),
                'chunk_id': item.properties.get('chunk_id', 0),
                'score': item.metadata.score if item.metadata else 0,
                'bm25_score': item.metadata.score if item.metadata else 0
            })

        return results

    def _search_hybrid(self, documentation, query: str, limit: int, alpha: float):
        """Perform hybrid search combining vector and BM25"""
        # Create embedding for query
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []

        # Hybrid search
        response = documentation.query.hybrid(
            query=query,
            vector=query_embedding,
            alpha=alpha,  # 0 = pure BM25, 1 = pure vector
            limit=limit,
            return_metadata=weaviate.classes.query.MetadataQuery(score=True)
        )

        # Format results
        results = []
        for item in response.objects:
            results.append({
                'content': item.properties.get('content', ''),
                'filename': item.properties.get('filename', ''),
                'title': item.properties.get('title', ''),
                'chunk_id': item.properties.get('chunk_id', 0),
                'score': item.metadata.score if item.metadata else 0,
                'hybrid_score': item.metadata.score if item.metadata else 0
            })

        return results

    def search_documents(self, query: str, top_k: int = 3, use_reranking: bool = None):
        """
        Search for relevant documents using configured search method

        Args:
            query: Search query
            top_k: Number of documents to return (used when reranking is disabled)
            use_reranking: Override settings.rag.rerank_enabled

        Returns:
            List of documents (reranked if enabled)
        """
        if not self.weaviate_client:
            self.connect_weaviate()

        if not self.weaviate_client:
            return []

        # Determine if we should use reranking
        if use_reranking is None:
            use_reranking = settings.rag.rerank_enabled

        # If reranking is enabled, retrieve more documents initially
        initial_top_k = settings.rag.initial_top_k if use_reranking else top_k

        try:
            # Get collection
            documentation = self.weaviate_client.collections.get("Documentation")

            # Check if collection has data
            collection_count = len(documentation)
            print(f"Documents in collection: {collection_count}")

            if collection_count == 0:
                print("⚠ Collection is empty. Load documents via loader.py")
                return []

            # Perform search based on configured method
            search_method = settings.rag.search_method.lower()
            print(f"[RAG] Using search method: {search_method}")

            if search_method == "vector":
                results = self._search_vector(documentation, query, initial_top_k)
            elif search_method == "bm25":
                results = self._search_bm25(documentation, query, initial_top_k)
            elif search_method == "hybrid":
                alpha = settings.rag.hybrid_alpha
                results = self._search_hybrid(documentation, query, initial_top_k, alpha)
            else:
                print(f"⚠ Unknown search method '{search_method}', falling back to vector search")
                results = self._search_vector(documentation, query, initial_top_k)

            print(f"[RAG] Initial retrieval: {len(results)} documents (method: {search_method})")

            # Apply reranking if enabled
            if use_reranking and results:
                final_top_k = settings.rag.final_top_k if use_reranking else top_k
                results = self.reranker.rerank(query, results, top_k=final_top_k)

            return results

        except Exception as e:
            import traceback
            print(f"✗ Search error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def generate_answer(self, query: str, context_docs: list) -> dict:
        """Generate answer using configured LLM"""
        if not context_docs:
            return {
                'answer': 'Sorry, I could not find relevant information in the documentation.',
                'sources': []
            }

        # Format context from found documents
        context = "\n\n---\n\n".join([
            f"Document: {doc['title']} ({doc['filename']})\n{doc['content']}"
            for doc in context_docs
        ])

        # System and user messages for chat completion
        system_message = """You are a technical support AI assistant. Your task is to answer user questions based on the provided website documentation.

Instructions:
1. Provide an accurate and helpful answer based ONLY on the provided documentation
2. If there is insufficient information, say so honestly
3. Answer in English
4. Be concise and specific
5. Use a friendly tone"""

        user_message = f"""Documentation:
{context}

User question: {query}

Please provide your answer:"""

        try:
            completion = self.llm_client.invoke([
                ("system", system_message),
                ("human", user_message)
            ])

            answer = completion.content

            # Format sources
            sources = [
                {
                    'title': doc['title'],
                    'filename': doc['filename']
                }
                for doc in context_docs
            ]

            # Remove duplicate sources
            unique_sources = []
            seen = set()
            for source in sources:
                key = (source['title'], source['filename'])
                if key not in seen:
                    seen.add(key)
                    unique_sources.append(source)

            return {
                'answer': answer,
                'sources': unique_sources
            }

        except Exception as e:
            print(f"✗ Error generating answer: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'answer': f'An error occurred while generating the answer: {str(e)}',
                'sources': []
            }

    def process_query(self, query: str) -> dict:
        """Full RAG pipeline: search + generation"""
        # Step 1: Search for relevant documents
        print(f"Query: {query}")
        docs = self.search_documents(query, top_k=3)
        print(f"Documents found: {len(docs)}")

        # Step 2: Generate answer
        result = self.generate_answer(query, docs)

        return result

    def get_stats(self) -> dict:
        """Get database statistics"""
        if not self.weaviate_client:
            self.connect_weaviate()

        try:
            documentation = self.weaviate_client.collections.get("Documentation")
            count = len(documentation)

            return {
                'total_chunks': count,
                'status': 'ok'
            }
        except Exception as e:
            return {
                'total_chunks': 0,
                'status': f'error: {str(e)}'
            }

    def close(self):
        """Close connections"""
        if self.weaviate_client:
            self.weaviate_client.close()
