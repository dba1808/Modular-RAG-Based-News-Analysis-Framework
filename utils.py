"""
Utility functions for the News Intelligence Platform.
"""

import time
import logging
import json
from functools import wraps
from datetime import datetime
from pathlib import Path

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


# ─── Bookmarks persistence ─────────────────────────────────
BOOKMARKS_FILE = "bookmarks.json"


def load_bookmarks() -> list:
    """Load bookmarks from file."""
    try:
        if Path(BOOKMARKS_FILE).exists():
            with open(BOOKMARKS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load bookmarks: {e}")
    return []


def save_bookmarks(bookmarks: list):
    """Save bookmarks to file."""
    try:
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(bookmarks, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save bookmarks: {e}")


def add_bookmark(title: str, url: str, source: str):
    """Add a bookmark."""
    bookmarks = load_bookmarks()
    # Avoid duplicates
    if not any(b.get("url") == url for b in bookmarks):
        bookmarks.insert(0, {
            "title": title,
            "url": url,
            "source": source,
            "saved_at": datetime.now().isoformat(),
        })
        save_bookmarks(bookmarks)
        return True
    return False


def remove_bookmark(url: str):
    """Remove a bookmark by URL."""
    bookmarks = load_bookmarks()
    bookmarks = [b for b in bookmarks if b.get("url") != url]
    save_bookmarks(bookmarks)


# ─── Conversation history persistence ──────────────────────
HISTORY_FILE = "chat_history.json"


def load_chat_history() -> list:
    """Load conversation history from file."""
    try:
        if Path(HISTORY_FILE).exists():
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load chat history: {e}")
    return []


def save_chat_history(chats: list):
    """Save conversation history to file."""
    try:
        # Keep only last 50 conversations
        with open(HISTORY_FILE, "w") as f:
            json.dump(chats[:50], f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Could not save chat history: {e}")
