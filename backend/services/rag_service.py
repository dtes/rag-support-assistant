"""
RAG Service - main logic for search and answer generation
Clean service - no env reading, all dependencies injected via constructor
"""
import weaviate
from typing import Optional
from sentence_transformers import SentenceTransformer
from infra.weaviate_client import WeaviateClient
from services.reranker_service import RerankerService


class RAGService:
    def __init__(
        self,
        llm_client,
        weaviate_client: WeaviateClient,
        reranker: RerankerService,
        embedding_model: str = "all-MiniLM-L6-v2",
        search_method: str = "vector",
        hybrid_alpha: float = 0.5,
        initial_top_k: int = 15,
        final_top_k: int = 7,
        rerank_enabled: bool = True
    ):
        """
        Initialize RAG service

        Args:
            llm_client: LLM client for answer generation
            weaviate_client: Weaviate client for vector search
            reranker: Reranker service
            embedding_model: Name of the sentence-transformers model
            search_method: Search method ("vector", "bm25", or "hybrid")
            hybrid_alpha: Weight for hybrid search (0=BM25, 1=vector)
            initial_top_k: Number of documents to retrieve initially
            final_top_k: Number of documents after reranking
            rerank_enabled: Whether to use reranking
        """
        self.llm_client = llm_client
        self.weaviate_client = weaviate_client
        self.reranker = reranker
        self.search_method = search_method
        self.hybrid_alpha = hybrid_alpha
        self.initial_top_k = initial_top_k
        self.final_top_k = final_top_k
        self.rerank_enabled = rerank_enabled

        # Load local embedding model
        print(f"Loading embedding model: {embedding_model}")
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            print("✓ Embedding model loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model '{embedding_model}': {e}")

    def get_embedding(self, text: str) -> list[float]:
        """Create embedding for text using local model"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"✗ Error creating embedding: {e}")
            return None

    def _search_vector(self, query: str, limit: int):
        """Perform vector (semantic) search"""
        # Create embedding for query
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []

        print(f"Query embedding dimension: {len(query_embedding)}")

        # Get collection
        documentation = self.weaviate_client.get_collection()

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

    def _search_bm25(self, query: str, limit: int):
        """Perform BM25 keyword search"""
        # Get collection
        documentation = self.weaviate_client.get_collection()

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

    def _search_hybrid(self, query: str, limit: int):
        """Perform hybrid search combining vector and BM25"""
        # Create embedding for query
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []

        # Get collection
        documentation = self.weaviate_client.get_collection()

        # Hybrid search
        response = documentation.query.hybrid(
            query=query,
            vector=query_embedding,
            alpha=self.hybrid_alpha,  # 0 = pure BM25, 1 = pure vector
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
            use_reranking: Override self.rerank_enabled

        Returns:
            List of documents (reranked if enabled)
        """
        if not self.weaviate_client.is_connected():
            print("⚠ Weaviate client not connected")
            return []

        # Determine if we should use reranking
        if use_reranking is None:
            use_reranking = self.rerank_enabled

        # If reranking is enabled, retrieve more documents initially
        initial_top_k = self.initial_top_k if use_reranking else top_k

        try:
            # Get collection
            documentation = self.weaviate_client.get_collection()

            # Check if collection has data
            collection_count = len(documentation)
            print(f"Documents in collection: {collection_count}")

            if collection_count == 0:
                print("⚠ Collection is empty. Load documents via loader.py")
                return []

            # Perform search based on configured method
            print(f"[RAG] Using search method: {self.search_method}")

            if self.search_method == "vector":
                results = self._search_vector(query, initial_top_k)
            elif self.search_method == "bm25":
                results = self._search_bm25(query, initial_top_k)
            elif self.search_method == "hybrid":
                results = self._search_hybrid(query, initial_top_k)
            else:
                print(f"⚠ Unknown search method '{self.search_method}', falling back to vector search")
                results = self._search_vector(query, initial_top_k)

            print(f"[RAG] Initial retrieval: {len(results)} documents (method: {self.search_method})")

            # Apply reranking if enabled
            if use_reranking and results:
                final_top_k = self.final_top_k if use_reranking else top_k
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
        try:
            documentation = self.weaviate_client.get_collection()
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
