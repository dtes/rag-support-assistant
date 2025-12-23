"""
Redis-based Checkpointer for LangGraph
Implements checkpointing using Redis for node-level caching
"""
import json
import pickle
from typing import Optional, Iterator, Tuple, Any, Dict
from datetime import datetime
import redis
from copy import deepcopy

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple

from config.settings import settings


class RedisCheckpointSaver(BaseCheckpointSaver):
    """
    Redis-based checkpoint saver for LangGraph

    Stores graph state checkpoints in Redis with automatic TTL.
    Each checkpoint is saved after a node execution and can be reused
    on subsequent runs with the same thread_id.
    """

    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        """
        Initialize Redis checkpoint saver

        Args:
            redis_client: Redis client instance
            ttl: Time-to-live for checkpoints in seconds (default: 1 hour)
        """
        super().__init__()
        self.redis_client = redis_client
        self.ttl = ttl
        print(f"✓ Redis checkpointer initialized (TTL: {ttl}s)")

    def _make_key(self, thread_id: str, checkpoint_ns: str = "", checkpoint_id: Optional[str] = None) -> str:
        """Generate Redis key for checkpoint"""
        if checkpoint_id:
            return f"checkpoint:{thread_id}:{checkpoint_ns}:{checkpoint_id}"
        return f"checkpoint:{thread_id}:{checkpoint_ns}"

    def _make_metadata_key(self, thread_id: str, checkpoint_ns: str = "", checkpoint_id: Optional[str] = None) -> str:
        """Generate Redis key for checkpoint metadata"""
        if checkpoint_id:
            return f"checkpoint_meta:{thread_id}:{checkpoint_ns}:{checkpoint_id}"
        return f"checkpoint_meta:{thread_id}:{checkpoint_ns}"

    def _clean_checkpoint_for_pickling(self, checkpoint: Checkpoint) -> Checkpoint:
        """
        Clean checkpoint by removing unpicklable objects

        Removes Langfuse trace objects and other non-serializable items
        """
        try:
            # Create a new checkpoint dict without deepcopy to avoid copying locks
            cleaned = {
                "v": checkpoint.get("v", 1),
                "id": checkpoint.get("id"),
                "ts": checkpoint.get("ts"),
                "channel_values": {},
                "channel_versions": checkpoint.get("channel_versions", {}),
                "versions_seen": checkpoint.get("versions_seen", {}),
                "pending_sends": checkpoint.get("pending_sends", []),
            }

            # Manually copy channel_values, excluding unpicklable objects
            if "channel_values" in checkpoint and checkpoint["channel_values"]:
                for key, value in checkpoint["channel_values"].items():
                    # Skip unpicklable objects
                    if key == "langfuse_trace":
                        cleaned["channel_values"][key] = None
                    elif key == "messages":
                        # Messages might contain unpicklable objects, copy carefully
                        try:
                            cleaned["channel_values"][key] = value
                        except:
                            cleaned["channel_values"][key] = []
                    else:
                        # Copy other simple values
                        try:
                            # Test if picklable
                            pickle.dumps(value)
                            cleaned["channel_values"][key] = value
                        except:
                            # If not picklable, store None
                            cleaned["channel_values"][key] = None

            return cleaned
        except Exception as e:
            print(f"[Checkpoint] Error cleaning checkpoint: {e}")
            return checkpoint

    def put(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        """
        Save checkpoint to Redis

        Args:
            config: Configuration dict containing thread_id
            checkpoint: Checkpoint object to save
            metadata: Checkpoint metadata
            new_versions: Version information

        Returns:
            Updated config dict
        """
        try:
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
            checkpoint_id = checkpoint["id"]

            # Clean and serialize checkpoint using pickle
            cleaned_checkpoint = self._clean_checkpoint_for_pickling(checkpoint)
            serialized_checkpoint = pickle.dumps(cleaned_checkpoint)
            serialized_metadata = pickle.dumps(metadata)

            # Save checkpoint
            checkpoint_key = self._make_key(thread_id, checkpoint_ns, checkpoint_id)
            metadata_key = self._make_metadata_key(thread_id, checkpoint_ns, checkpoint_id)

            # Store in Redis with TTL
            self.redis_client.setex(
                checkpoint_key,
                self.ttl,
                serialized_checkpoint
            )

            self.redis_client.setex(
                metadata_key,
                self.ttl,
                serialized_metadata
            )

            # Also save as "latest" checkpoint for this thread
            latest_key = self._make_key(thread_id, checkpoint_ns, "latest")
            latest_meta_key = self._make_metadata_key(thread_id, checkpoint_ns, "latest")

            self.redis_client.setex(latest_key, self.ttl, serialized_checkpoint)
            self.redis_client.setex(latest_meta_key, self.ttl, serialized_metadata)

            print(f"[Checkpoint] Saved: {checkpoint_id[:8]}... for thread {thread_id}")

            return {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                }
            }

        except Exception as e:
            print(f"[Checkpoint] Error saving: {e}")
            return config

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """
        Retrieve checkpoint from Redis

        Args:
            config: Configuration dict containing thread_id

        Returns:
            CheckpointTuple if found, None otherwise
        """
        try:
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
            checkpoint_id = config["configurable"].get("checkpoint_id")

            # If specific checkpoint_id not provided, get latest
            if not checkpoint_id:
                checkpoint_id = "latest"

            checkpoint_key = self._make_key(thread_id, checkpoint_ns, checkpoint_id)
            metadata_key = self._make_metadata_key(thread_id, checkpoint_ns, checkpoint_id)

            # Retrieve from Redis
            serialized_checkpoint = self.redis_client.get(checkpoint_key)
            serialized_metadata = self.redis_client.get(metadata_key)

            if not serialized_checkpoint:
                print(f"[Checkpoint] Not found for thread {thread_id}")
                return None

            # Deserialize
            checkpoint = pickle.loads(serialized_checkpoint)
            metadata = pickle.loads(serialized_metadata) if serialized_metadata else {}

            print(f"[Checkpoint] Retrieved for thread {thread_id}")

            return CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": checkpoint["id"],
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=None,  # We don't track parent checkpoints for simplicity
            )

        except Exception as e:
            print(f"[Checkpoint] Error retrieving: {e}")
            return None

    def list(
        self,
        config: Optional[dict] = None,
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """
        List checkpoints (simplified implementation)

        For Redis implementation, we primarily use get_tuple,
        but this method is required by the base class.
        """
        if not config:
            return

        # Just return the latest checkpoint if it exists
        checkpoint_tuple = self.get_tuple(config)
        if checkpoint_tuple:
            yield checkpoint_tuple

    def put_writes(
        self,
        config: dict,
        writes: list,
        task_id: str,
    ) -> None:
        """
        Store pending writes (not implemented for basic caching)

        This is used for more advanced checkpoint features.
        For basic node-level caching, we don't need this.
        """
        pass


# Global checkpointer instance
_checkpointer: Optional[RedisCheckpointSaver] = None


def get_redis_checkpointer() -> Optional[RedisCheckpointSaver]:
    """
    Get or create Redis checkpointer instance

    Returns:
        RedisCheckpointSaver instance or None if Redis unavailable
    """
    global _checkpointer

    if _checkpointer is None:
        try:
            # Get Redis client
            redis_client = redis.from_url(
                settings.redis.url,
                decode_responses=False  # Need binary mode for serialization
            )

            # Test connection
            redis_client.ping()

            # Create checkpointer with configured TTL
            _checkpointer = RedisCheckpointSaver(
                redis_client=redis_client,
                ttl=settings.redis.ttl_checkpoints
            )

        except Exception as e:
            print(f"✗ Failed to initialize Redis checkpointer: {e}")
            _checkpointer = None

    return _checkpointer
