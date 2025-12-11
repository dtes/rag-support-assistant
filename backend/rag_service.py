"""
RAG Service - main logic for search and answer generation
"""
import os
import weaviate
from openai import OpenAI, AzureOpenAI
from sentence_transformers import SentenceTransformer

# Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "openai"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # Optional, defaults to api.openai.com
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

# Ollama Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight and fast local model

class RAGService:
    def __init__(self):
        """Initialize the service"""
        self.weaviate_client = None
        self.llm_provider = LLM_PROVIDER.lower()

        # Initialize LLM client based on provider
        if self.llm_provider == "openai":
            # Use OpenAI cloud API
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

            base_url = OPENAI_BASE_URL if OPENAI_BASE_URL else "https://api.openai.com/v1"
            self.llm_client = AzureOpenAI(azure_endpoint=base_url, api_key=OPENAI_API_KEY, api_version="2024-02-01",)
            self.llm_model = OPENAI_MODEL
            print(f"✓ Using OpenAI API at {base_url} with model: {self.llm_model}")
        else:
            # Use local Ollama
            self.llm_client = OpenAI(
                base_url=f"{OLLAMA_URL}/v1",
                api_key="ollama"  # Ollama doesn't require a real API key
            )
            self.llm_model = OLLAMA_MODEL
            print(f"✓ Using local Ollama at {OLLAMA_URL} with model: {self.llm_model}")

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
        """Generate answer using configured LLM (Ollama or OpenAI) via OpenAI SDK"""
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
            # Use OpenAI SDK (works for both OpenAI and Ollama)
            completion = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            answer = completion.choices[0].message.content

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
