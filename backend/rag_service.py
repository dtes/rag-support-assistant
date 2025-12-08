"""
RAG Service - main logic for search and answer generation
"""
import os
import weaviate
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer

# Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight and fast local model

class RAGService:
    def __init__(self):
        """Initialize the service"""
        self.weaviate_client = None
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Load local embedding model
        print(f"Loading local embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print("✓ Local embedding model loaded")

        self.connect_weaviate()

    def connect_weaviate(self):
        """Connect to Weaviate"""
        try:
            self.weaviate_client = weaviate.connect_to_custom(
                http_host="weaviate",
                http_port=8080,
                http_secure=False,
                grpc_host="weaviate",
                grpc_port=50051,
                grpc_secure=False,
            )
            print("✓ Connected to Weaviate")
        except Exception as e:
            print(f"✗ Error connecting to Weaviate: {e}")
            self.weaviate_client = None

    def get_embedding(self, text: str) -> list[float]:
        """Create embedding for text using local model"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"✗ Error creating embedding: {e}")
            return None

    def search_documents(self, query: str, top_k: int = 3):
        """Search for relevant documents"""
        if not self.weaviate_client:
            self.connect_weaviate()

        if not self.weaviate_client:
            return []

        try:
            # Create embedding for query
            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return []

            print(f"Query embedding dimension: {len(query_embedding)}")

            # Get collection
            documentation = self.weaviate_client.collections.get("Documentation")

            # Check if collection has data
            collection_count = len(documentation)
            print(f"Documents in collection: {collection_count}")

            if collection_count == 0:
                print("⚠ Collection is empty. Load documents via loader.py")
                return []

            # Vector search
            response = documentation.query.near_vector(
                near_vector=query_embedding,
                limit=top_k,
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
                    'distance': item.metadata.distance if item.metadata else None
                })

            return results

        except Exception as e:
            import traceback
            print(f"✗ Search error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def generate_answer(self, query: str, context_docs: list) -> dict:
        """Generate answer using Claude"""
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

        # Prompt for Claude
        prompt = f"""You are a technical support AI assistant. Your task is to answer user questions based on the provided website documentation.

Documentation:
{context}

User question: {query}

Instructions:
1. Provide an accurate and helpful answer based ONLY on the provided documentation
2. If there is insufficient information, say so honestly
3. Answer in English
4. Be concise and specific
5. Use a friendly tone

Answer:"""

        try:
            # Request to Claude API
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            answer = message.content[0].text

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
