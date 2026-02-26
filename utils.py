"""
Utility functions for the News RAG system.
"""

import time
import logging
from functools import wraps
from datetime import datetime

logger = logging.getLogger("news_rag.utils")


def timer(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"⏱  {func.__name__} executed in {elapsed:.2f}s")
        return result, elapsed
    return wrapper


def format_timestamp(iso_str: str) -> str:
    """Convert ISO timestamp to a readable format."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except Exception:
        return iso_str


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "…"
