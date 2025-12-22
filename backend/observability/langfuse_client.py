"""
LangFuse integration for observability and tracing
"""
from typing import Optional, Any
from config.settings import settings


class LangFuseClient:
    """Singleton LangFuse client for tracing"""

    _instance: Optional[Any] = None

    @classmethod
    def get_client(cls) -> Optional[Any]:
        """
        Get or create LangFuse client instance
        Returns None if LangFuse is not configured
        """
        if not settings.langfuse.enabled:
            print("⚠ LangFuse is not configured (missing public/secret keys)")
            return None

        if cls._instance is None:
            try:
                from langfuse import Langfuse
                import os

                # Disable OpenTelemetry export to avoid 404 errors
                # LangFuse 3.x uses OpenTelemetry internally but we don't need OTLP export
                os.environ.setdefault("OTEL_SDK_DISABLED", "false")

                cls._instance = Langfuse(
                    public_key=settings.langfuse.public_key,
                    secret_key=settings.langfuse.secret_key,
                    host=settings.langfuse.host,
                    debug=False,
                    # Disable OpenTelemetry tracer provider to prevent 404 errors
                    tracer_provider=None,
                )
                print(f"✓ LangFuse client initialized (host: {settings.langfuse.host})")
            except ImportError as ie:
                print(f"⚠ LangFuse package not installed or incompatible version: {ie}")
                return None
            except Exception as e:
                print(f"✗ Failed to initialize LangFuse: {e}")
                return None

        return cls._instance

    @classmethod
    def get_handler(cls) -> Optional[Any]:
        """
        Get LangFuse client (for backward compatibility)
        In LangFuse 3.x, use @observe decorator instead of callbacks
        """
        return cls.get_client()

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if LangFuse is enabled and configured"""
        return settings.langfuse.enabled


# Convenience function
def get_langfuse_handler() -> Optional[Any]:
    """
    Get LangFuse client (backward compatibility)
    Note: In LangFuse 3.x, callbacks are deprecated.
    Use LangFuseClient.get_client() and manual tracing instead.
    """
    return LangFuseClient.get_client()
