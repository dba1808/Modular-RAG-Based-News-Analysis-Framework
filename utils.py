"""
Utility functions for the News Intelligence Platform.
"""

import time
import logging
import json
import re
from functools import wraps
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

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


# ─── Per-User Storage Helpers ──────────────────────────────
USER_DATA_DIR = Path(__file__).parent / "user_data"


def _get_user_storage_dir(username: Optional[str] = None) -> Path:
    """Return user-isolated directory for state storage (bookmarks, chats)."""
    if not username:
        try:
            import streamlit as st
            username = st.session_state.get("user_profile", {}).get("username")
        except Exception:
            pass
    safe_user = re.sub(r"[^a-zA-Z0-9_-]", "_", str(username or "guest").lower())
    p = USER_DATA_DIR / safe_user
    p.mkdir(parents=True, exist_ok=True)
    return p


# ─── Bookmarks persistence ─────────────────────────────────
def load_bookmarks(username: Optional[str] = None) -> list:
    """Load bookmarks isolated to the given or active user."""
    b_file = _get_user_storage_dir(username) / "bookmarks.json"
    try:
        if b_file.exists():
            with open(b_file, "r", encoding="utf-8") as f:
                return json.load(f)
        # Migrate from legacy single-user file if available and user is default
        legacy = Path("bookmarks.json")
        if legacy.exists() and (username in ("admin", "guest") or not username):
            with open(legacy, "r", encoding="utf-8") as f:
                data = json.load(f)
                save_bookmarks(data, username)
                return data
    except Exception as e:
        logger.warning(f"Could not load bookmarks: {e}")
    return []


def save_bookmarks(bookmarks: list, username: Optional[str] = None):
    """Save bookmarks isolated to the given or active user."""
    b_file = _get_user_storage_dir(username) / "bookmarks.json"
    try:
        with open(b_file, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Could not save bookmarks: {e}")


def add_bookmark(title: str, url: str, source: str, username: Optional[str] = None) -> bool:
    """Add a bookmark for the given or active user."""
    bookmarks = load_bookmarks(username)
    # Avoid duplicates
    if not any(b.get("url") == url for b in bookmarks):
        bookmarks.insert(0, {
            "title": title,
            "url": url,
            "source": source,
            "saved_at": datetime.now().isoformat(),
        })
        save_bookmarks(bookmarks, username)
        return True
    return False


def remove_bookmark(url: str, username: Optional[str] = None):
    """Remove a bookmark by URL for the given or active user."""
    bookmarks = load_bookmarks(username)
    bookmarks = [b for b in bookmarks if b.get("url") != url]
    save_bookmarks(bookmarks, username)


# ─── Conversation history persistence ──────────────────────
def load_chat_history(username: Optional[str] = None) -> list:
    """Load conversation history isolated to the given or active user."""
    h_file = _get_user_storage_dir(username) / "chat_history.json"
    try:
        if h_file.exists():
            with open(h_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load chat history: {e}")
    return []


def save_chat_history(chats: list, username: Optional[str] = None):
    """Save conversation history isolated to the given or active user."""
    h_file = _get_user_storage_dir(username) / "chat_history.json"
    try:
        # Keep only last 50 conversations
        with open(h_file, "w", encoding="utf-8") as f:
            json.dump(chats[:50], f, indent=2, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Could not save chat history: {e}")
