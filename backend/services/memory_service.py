"""
Chat Memory Service - manages conversation history using Redis
"""
import json
from typing import List, Dict, Optional
from datetime import datetime
import redis
from config.settings import settings


class MemoryService:
    """Redis-based chat memory service"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.redis.url,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            print("✓ Redis memory service initialized")
        except Exception as e:
            print(f"✗ Failed to connect to Redis: {e}")
            self.redis_client = None

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
        if not self.redis_client:
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
            self.redis_client.rpush(key, json.dumps(message, ensure_ascii=False))

            # Set TTL (24 hours)
            self.redis_client.expire(key, 86400)

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
        if not self.redis_client:
            return []

        try:
            key = self._get_key(session_id)

            # Get all messages
            if limit:
                # Get last N messages
                messages_raw = self.redis_client.lrange(key, -limit, -1)
            else:
                # Get all messages
                messages_raw = self.redis_client.lrange(key, 0, -1)

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
        if not self.redis_client:
            return False

        try:
            key = self._get_key(session_id)
            self.redis_client.delete(key)
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
        if not self.redis_client:
            return {"message_count": 0}

        try:
            key = self._get_key(session_id)
            count = self.redis_client.llen(key)
            ttl = self.redis_client.ttl(key)

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
