"""
FastAPI Dependencies - thin layer for dependency injection
"""
from typing import Annotated
from fastapi import Depends
from context import AppContext


# Global app context (set during startup in main.py)
_app_context: AppContext = None


def get_context() -> AppContext:
    """
    Get global application context

    Returns:
        AppContext instance

    Raises:
        RuntimeError: If context not initialized
    """
    if _app_context is None:
        raise RuntimeError("AppContext not initialized. Call set_context() during startup.")
    return _app_context


def set_context(ctx: AppContext) -> None:
    """
    Set global application context (called from main.py startup)

    Args:
        ctx: AppContext instance
    """
    global _app_context
    _app_context = ctx


# Type alias for cleaner code in route handlers
AppContextDep = Annotated[AppContext, Depends(get_context)]
