"""
News Fetcher — Free RSS Edition
────────────────────────────────
Fetches live news from free RSS feeds (BBC, Reuters, Google News, etc.)
NO API KEY REQUIRED.
Falls back to NewsAPI only if NEWS_API_KEY is configured.
"""

import time
import logging
import re
import feedparser
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any
from langchain.schema import Document

logger = logging.getLogger("news_rag.fetcher")

# ─── In-memory cache ─────────────────────────────────────────
_cache: Dict[str, Any] = {}
CACHE_TTL = 900  # 15 minutes

# ─── Free RSS Feeds (no key needed) ──────────────────────────
# Google News RSS supports any search query for free
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

# Topic-specific free RSS feeds
TOPIC_RSS_FEEDS = {
    "technology":   ["https://feeds.feedburner.com/TechCrunch",
                     "https://www.wired.com/feed/rss",
                     "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"],
    "business":     ["https://feeds.bbci.co.uk/news/business/rss.xml",
                     "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"],
    "sports":       ["https://feeds.bbci.co.uk/sport/rss.xml"],
    "health":       ["https://feeds.bbci.co.uk/news/health/rss.xml",
                     "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"],
    "science":      ["https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
                     "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"],
    "world":        ["https://feeds.bbci.co.uk/news/world/rss.xml",
                     "https://rss.reuters.com/reuters/worldNews"],
    "cricket":      ["https://www.espncricinfo.com/rss/content/story/feeds/0.xml"],
    "politics":     ["https://feeds.bbci.co.uk/news/politics/rss.xml",
                     "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"],
    "finance":      ["https://feeds.bbci.co.uk/news/business/rss.xml"],
    "entertainment":["https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"],
    "default":      ["https://feeds.bbci.co.uk/news/rss.xml",
                     "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"],
}


def _clean(text: str) -> str:
    """Strip HTML tags from text."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def _cache_key(topic: str) -> str:
    return topic.lower().strip()


def _is_fresh(key: str) -> bool:
    if key not in _cache:
        return False
    return (time.time() - _cache[key]["ts"]) < CACHE_TTL


def _detect_topic(query: str) -> str:
    """Map query keywords to known topic buckets."""
    q = query.lower()
    mapping = {
        "cricket": ["cricket", "t20", "ipl", "odi", "test match", "bcci", "virat", "rohit"],
        "technology": ["tech", "ai", "artificial intelligence", "software", "apple", "google",
                       "microsoft", "startup", "coding", "computer"],
        "business":   ["business", "economy", "trade", "company", "market", "gdp", "startup"],
        "sports":     ["sport", "football", "soccer", "tennis", "hockey", "basketball", "olympics"],
        "health":     ["health", "medical", "hospital", "disease", "vaccine", "covid", "doctor"],
        "science":    ["science", "space", "nasa", "climate", "research", "discovery"],
        "world":      ["world", "international", "global", "war", "conflict", "ukraine", "russia"],
        "politics":   ["politics", "election", "government", "parliament", "minister", "president"],
        "finance":    ["finance", "stock", "gold", "price", "bank", "invest", "rupee", "dollar"],
        "entertainment": ["movie", "film", "celebrity", "bollywood", "hollywood", "music", "actor"],
    }
    for topic, keywords in mapping.items():
        if any(kw in q for kw in keywords):
            return topic
    return "default"


def _fetch_rss(url: str, max_items: int = 10) -> List[Document]:
    """Parse an RSS feed and return LangChain Documents."""
    docs = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_items]:
            title   = _clean(getattr(entry, "title", ""))
            summary = _clean(getattr(entry, "summary", ""))
            link    = getattr(entry, "link", "")
            source  = getattr(feed.feed, "title", url)
            pub     = getattr(entry, "published", "")

            if not title:
                continue

            content = f"Title: {title}\n\nSummary: {summary}"
            docs.append(Document(
                page_content=content,
                metadata={"title": title, "url": link, "source": source, "date": pub},
            ))
    except Exception as e:
        logger.warning(f"RSS feed failed ({url}): {e}")
    return docs


def _fetch_google_news_rss(query: str, max_items: int = 15) -> List[Document]:
    """Use Google News RSS to search any topic — completely free."""
    url = GOOGLE_NEWS_RSS.format(query=requests.utils.quote(query))
    return _fetch_rss(url, max_items)


def fetch_news(topic: str = "latest news", hours: int = 48) -> List[Document]:
    """
    Fetch news articles for the given topic/query.
    Uses free RSS feeds — no API key required.
    """
    key = _cache_key(topic)
    if _is_fresh(key):
        logger.info(f"📦 Cache hit: '{topic}' ({len(_cache[key]['data'])} docs)")
        return _cache[key]["data"]

    docs: List[Document] = []

    # 1. Google News RSS (topic-aware search)
    logger.info(f"📡 Google News RSS search: '{topic}'")
    docs = _fetch_google_news_rss(topic, max_items=15)

    # 2. Fall back to topic-specific RSS feeds if Google News is sparse
    if len(docs) < 5:
        detected = _detect_topic(topic)
        feeds = TOPIC_RSS_FEEDS.get(detected, TOPIC_RSS_FEEDS["default"])
        for feed_url in feeds:
            logger.info(f"📡 Fallback RSS: {feed_url}")
            docs += _fetch_rss(feed_url, max_items=8)
            if len(docs) >= 10:
                break

    # 3. Final fallback — global default feeds
    if len(docs) < 3:
        for feed_url in TOPIC_RSS_FEEDS["default"]:
            docs += _fetch_rss(feed_url, max_items=8)

    # Deduplicate by title
    seen = set()
    unique = []
    for d in docs:
        t = d.metadata.get("title", "")
        if t and t not in seen:
            seen.add(t)
            unique.append(d)

    logger.info(f"✅ Total unique articles: {len(unique)}")
    _cache[key] = {"data": unique, "ts": time.time()}
    return unique


def clear_cache():
    _cache.clear()
    logger.info("🗑  News cache cleared")


def get_available_topics() -> List[str]:
    return [
        "Technology", "Business", "Science", "Health",
        "Sports", "Cricket", "Entertainment", "Politics",
        "World", "Finance",
    ]
