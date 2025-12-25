"""
Chat Memory Service - manages conversation history using Redis or in-memory storage
"""
import json
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
import redis
from config.settings import settings


class InMemoryStore:
    """In-memory storage for chat history"""

    def __init__(self):
        """Initialize in-memory store"""
        self.store: Dict[str, List[str]] = defaultdict(list)
        self.ttls: Dict[str, datetime] = {}

    def rpush(self, key: str, value: str) -> None:
        """Append value to list"""
        self.store[key].append(value)

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Get range of values from list"""
        if key not in self.store:
            return []

        # Check TTL
        if key in self.ttls:
            if datetime.now() > self.ttls[key]:
                # Expired
                del self.store[key]
                del self.ttls[key]
                return []

        items = self.store[key]
        if end == -1:
            return items[start:]
        return items[start:end+1]

    def llen(self, key: str) -> int:
        """Get length of list"""
        if key not in self.store:
            return 0

        # Check TTL
        if key in self.ttls:
            if datetime.now() > self.ttls[key]:
                del self.store[key]
                del self.ttls[key]
                return 0

        return len(self.store[key])

    def expire(self, key: str, seconds: int) -> None:
        """Set TTL for key"""
        from datetime import timedelta
        self.ttls[key] = datetime.now() + timedelta(seconds=seconds)

    def delete(self, key: str) -> None:
        """Delete key"""
        if key in self.store:
            del self.store[key]
        if key in self.ttls:
            del self.ttls[key]

    def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds"""
        if key not in self.ttls:
            return -1

        remaining = (self.ttls[key] - datetime.now()).total_seconds()
        return int(remaining) if remaining > 0 else -2


class MemoryService:
    """Chat memory service with Redis or in-memory backend"""

    def __init__(self):
        """Initialize memory service based on configuration"""
        self.memory_type = settings.redis.memory_type

        if self.memory_type == "redis":
            try:
                self.client = redis.from_url(
                    settings.redis.url,
                    decode_responses=True
                )
                # Test connection
                self.client.ping()
                print("✓ Redis memory service initialized")
            except Exception as e:
                print(f"✗ Failed to connect to Redis: {e}")
                print("✓ Falling back to in-memory storage")
                self.memory_type = "memory"
                self.client = InMemoryStore()
        else:
            self.client = InMemoryStore()
            print("✓ In-memory storage initialized for chat history")

    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"chat_history:{session_id}"

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add message to chat history

        Args:
            session_id: Session identifier
            role: "user" or "assistant"
            content: Message content
            metadata: Optional metadata (query_type, sources, etc.)

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            key = self._get_key(session_id)

            # Append message to list
            self.client.rpush(key, json.dumps(message, ensure_ascii=False))

            # Set TTL (24 hours)
            self.client.expire(key, 86400)

            return True

        except Exception as e:
            print(f"✗ Failed to add message to memory: {e}")
            return False

    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get chat history for session

        Args:
            session_id: Session identifier
            limit: Optional limit (get last N messages)

        Returns:
            List of messages in chronological order
        """
        if not self.client:
            return []

        try:
            key = self._get_key(session_id)

            # Get all messages
            if limit:
                # Get last N messages
                messages_raw = self.client.lrange(key, -limit, -1)
            else:
                # Get all messages
                messages_raw = self.client.lrange(key, 0, -1)

            # Parse messages
            messages = []
            for msg_raw in messages_raw:
                try:
                    msg = json.loads(msg_raw)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue

            return messages

        except Exception as e:
            print(f"✗ Failed to get history: {e}")
            return []

    def get_messages_for_llm(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[tuple]:
        """
        Get chat history formatted for LLM (LangChain format)

        Args:
            session_id: Session identifier
            limit: Number of recent messages to retrieve

        Returns:
            List of (role, content) tuples
        """
        history = self.get_history(session_id, limit=limit)

        llm_messages = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Convert to LangChain format
            if role == "user":
                llm_messages.append(("human", content))
            elif role == "assistant":
                llm_messages.append(("ai", content))

        return llm_messages

    def clear_history(self, session_id: str) -> bool:
        """
        Clear chat history for session

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            key = self._get_key(session_id)
            self.client.delete(key)
            return True

        except Exception as e:
            print(f"✗ Failed to clear history: {e}")
            return False

    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get statistics for session

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with stats
        """
        if not self.client:
            return {"message_count": 0}

        try:
            key = self._get_key(session_id)
            count = self.client.llen(key)
            ttl = self.client.ttl(key)

            return {
                "message_count": count,
                "ttl_seconds": ttl if ttl > 0 else None
            }

        except Exception as e:
            print(f"✗ Failed to get stats: {e}")
            return {"message_count": 0}


# Global instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create memory service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
