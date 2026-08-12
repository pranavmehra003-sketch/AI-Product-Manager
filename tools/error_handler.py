"""
Error handler tool — retry logic, error logging, and human alerts.
"""
from __future__ import annotations
import time
import functools
from typing import Any, Callable, Optional, Type
from datetime import datetime


MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def with_retry(
    max_retries: int = MAX_RETRIES,
    delay: float = RETRY_DELAY_SECONDS,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    """Decorator: automatically retry a function on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error: Optional[Exception] = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries:
                        time.sleep(delay * attempt)
                    else:
                        raise RuntimeError(
                            f"[{func.__name__}] Failed after {max_retries} retries. "
                            f"Last error: {e}"
                        ) from e
            raise last_error  # type: ignore
        return wrapper
    return decorator


def log_error(
    agent_name: str,
    session_id: str,
    error_message: str,
    retry_count: int = 0,
    status: str = "failed",
) -> dict:
    """Create a structured error log entry."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "session_id": session_id,
        "error_message": str(error_message),
        "retry_count": retry_count,
        "status": status,
    }
    print(f"[ERROR LOG] {agent_name} | {error_message[:120]}")
    return entry


def safe_call(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """Call a function safely; return default value on any exception."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[SAFE CALL] {func.__name__} failed: {e}")
        return default
