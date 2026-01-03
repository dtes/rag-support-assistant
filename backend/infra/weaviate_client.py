"""
Weaviate Client - clean infrastructure component
No env reading, all configuration passed via constructor
"""
import weaviate
from typing import Optional


class WeaviateClient:
    """Weaviate vector database client"""

    def __init__(self, url: str, collection_name: str):
        """
        Initialize Weaviate client

        Args:
            url: Weaviate URL (e.g., "http://weaviate:8080")
            collection_name: Collection name (e.g., "Documentation")
        """
        self.url = url
        self.collection_name = collection_name
        self._client: Optional[weaviate.WeaviateClient] = None

    def connect(self) -> None:
        """Connect to Weaviate"""
        try:
            # Parse URL to extract host and port
            from urllib.parse import urlparse
            parsed = urlparse(self.url)
            host = parsed.hostname or "weaviate"
            http_port = parsed.port or 8080

            self._client = weaviate.connect_to_custom(
                http_host=host,
                http_port=http_port,
                http_secure=False,
                grpc_host=host,
                grpc_port=50051,
                grpc_secure=False,
            )
            print(f"✓ Connected to Weaviate at {self.url}")
        except Exception as e:
            print(f"✗ Error connecting to Weaviate: {e}")
            raise

    def close(self) -> None:
        """Close Weaviate connection"""
        if self._client:
            self._client.close()
            print("✓ Weaviate connection closed")

    def is_connected(self) -> bool:
        """Check if connected to Weaviate"""
        return self._client is not None

    @property
    def client(self) -> weaviate.WeaviateClient:
        """Get Weaviate client instance"""
        if not self._client:
            raise RuntimeError("Weaviate client not connected. Call connect() first.")
        return self._client

    def get_collection(self):
        """Get collection by name"""
        return self.client.collections.get(self.collection_name)
