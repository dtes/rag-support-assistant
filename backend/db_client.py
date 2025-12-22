import os
import weaviate

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

def connect_weaviate():
    """Connect to Weaviate"""
    try:
        weaviate_client = weaviate.connect_to_custom(
            http_host="weaviate",
            http_port=8080,
            http_secure=False,
            grpc_host="weaviate",
            grpc_port=50051,
            grpc_secure=False,
        )
        print("✓ Connected to Weaviate")

        return weaviate_client
    except Exception as e:
        print(f"✗ Error connecting to Weaviate: {e}")

