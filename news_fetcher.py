"""
News Fetcher — Multi-Source Intelligence Edition
─────────────────────────────────────────────────
Fetches live news from multiple reliable sources:
  • Google News RSS (query & location aware)
  • Topic-specific RSS feeds (BBC, NYT, TechCrunch, Wired, etc.)
  • GNews API (optional fallback if key provided)
Includes advanced multi-signal deduplication, source extraction,
reliability scoring, and category tagging.
NO API KEY REQUIRED for core operation.
"""

import time
import logging
import re
import hashlib
from difflib import SequenceMatcher
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Set
import feedparser
import requests
from langchain_core.documents import Document

from config import (
    GNEWS_API_KEY,
    GNEWS_API_BASE_URL,
    NEWS_CACHE_TTL_SECONDS,
    SOURCE_RELIABILITY_SCORES,
)

logger = logging.getLogger("news_rag.fetcher")

# ─── In-memory cache ─────────────────────────────────────────
_cache: Dict[str, Any] = {}
CACHE_TTL = NEWS_CACHE_TTL_SECONDS

# ─── Free RSS Feeds ──────────────────────────────────────────
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={gl}:{lang}"

TOPIC_RSS_FEEDS = {
    "technology": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    ],
    "business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    ],
    "health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
    ],
    "science": [
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    ],
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ],
    "cricket": [
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    ],
    "politics": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    ],
    "finance": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
    ],
    "entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    ],
    "ai": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
    ],
    "default": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    ],
}


import html as py_html


def _clean(text: str) -> str:
    """Strip HTML tags, unescape HTML entities, and normalize whitespace."""
    if not text:
        return ""
    text = py_html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    return " ".join(text.split()).strip()


def _normalize_url(url: str) -> str:
    """Remove tracking parameters (utm_*, etc.) from article URLs."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        query_dict = parse_qs(parsed.query)
        cleaned_query = {k: v for k, v in query_dict.items() if not k.lower().startswith("utm_") and k.lower() not in ("oc", "ved")}
        new_query = urlencode(cleaned_query, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ""))
    except Exception:
        return url


def _cache_key(topic: str, gl: str = "IN") -> str:
    return f"{topic.lower().strip()}::{gl.upper()}"


def _is_fresh(key: str) -> bool:
    if key not in _cache:
        return False
    return (time.time() - _cache[key]["ts"]) < CACHE_TTL


def _parse_pub_date(date_str: str) -> Optional[datetime]:
    """Parse various RSS date formats into timezone-aware UTC datetime."""
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            continue
    return None


def format_time_ago(dt_input) -> str:
    """Convert a datetime or string to a user-friendly '2h ago' format."""
    if not dt_input:
        return "Recent"
    dt = dt_input
    if isinstance(dt_input, str):
        dt = _parse_pub_date(dt_input)
    if not dt:
        return "Recent"
    try:
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0:
            return "Just now"
        if seconds < 60:
            return f"{seconds}s ago"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days < 7:
            return f"{days}d ago"
        return dt.strftime("%b %d")
    except Exception:
        return "Recent"


def get_source_reliability(source_name: str) -> float:
    """Compute reliability score (0.0 to 1.0) for a given news source."""
    if not source_name:
        return SOURCE_RELIABILITY_SCORES.get("default", 0.60)
    s = source_name.lower().strip()
    for name, score in SOURCE_RELIABILITY_SCORES.items():
        if name in s or s in name:
            return score
    return SOURCE_RELIABILITY_SCORES.get("default", 0.60)


def _detect_category(title: str, content: str = "") -> str:
    """Assign category based on keywords in title and content."""
    text = f"{title} {content}".lower()
    categories = [
        ("AI & Technology", ["ai", "artificial intelligence", "gpt", "nvidia", "software", "tech", "algorithm", "robotics", "meta", "google", "apple", "microsoft", "chip", "semiconductor", "cyber"]),
        ("Markets & Economy", ["stock", "market", "sensex", "nifty", "nasdaq", "dow", "inflation", "gdp", "economy", "bank", "invest", "crypto", "bitcoin", "rupee", "dollar", "trade"]),
        ("Politics & Policy", ["election", "parliament", "government", "minister", "modi", "biden", "trump", "senate", "policy", "court", "supreme court", "legislation", "cabinet"]),
        ("Science & Climate", ["climate", "space", "isro", "nasa", "planet", "galaxy", "carbon", "renewable", "earthquake", "weather", "scientist", "discovery"]),
        ("Health & Medicine", ["health", "vaccine", "doctor", "medical", "hospital", "cancer", "disease", "treatment", "fda", "who", "virus"]),
        ("Sports", ["cricket", "ipl", "football", "soccer", "tennis", "goal", "wicket", "match", "championship", "tournament", "olympics"]),
        ("World Affairs", ["war", "conflict", "diplomacy", "summit", "nato", "un", "ukraine", "russia", "china", "israel", "gaza", "sanctions"]),
    ]
    for cat_name, kws in categories:
        if any(kw in text for kw in kws):
            return cat_name
    return "General News"


# ─── Advanced Deduplication ───────────────────────────────────
def _title_tokens(title: str) -> Set[str]:
    """Extract meaningful lowercased token set from title."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    stop = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "is", "are", "was", "with", "by", "from", "says", "new", "after", "its", "it"}
    return {w for w in words if len(w) > 2 and w not in stop}


def _is_duplicate_article(title: str, url: str, seen_articles: List[Dict[str, Any]]) -> bool:
    """
    Multi-signal deduplication:
    1. Exact or normalized URL match.
    2. Fuzzy string ratio (SequenceMatcher >= 0.76).
    3. Token-set Jaccard overlap >= 0.68.
    """
    clean_url = _normalize_url(url)
    tokens = _title_tokens(title)
    norm_title = re.sub(r"[^a-z0-9\s]", "", title.lower()).strip()

    for item in seen_articles:
        # Check URL
        if clean_url and item.get("clean_url") and clean_url == item.get("clean_url"):
            return True

        # Check String ratio
        seen_norm = item.get("norm_title", "")
        ratio = SequenceMatcher(None, norm_title, seen_norm).ratio()
        if ratio >= 0.76:
            return True

        # Check token Jaccard similarity
        seen_tokens = item.get("tokens", set())
        if tokens and seen_tokens:
            intersection = len(tokens & seen_tokens)
            union = len(tokens | seen_tokens)
            if union > 0 and (intersection / union) >= 0.68:
                return True

    return False


def _deduplicate(docs: List[Document]) -> List[Document]:
    """Deduplicate document list while prioritizing higher reliability / richer articles."""
    seen: List[Dict[str, Any]] = []
    unique: List[Document] = []

    for d in docs:
        title = d.metadata.get("title", "").strip()
        url = d.metadata.get("url", "")
        if not title:
            continue

        if not _is_duplicate_article(title, url, seen):
            seen.append({
                "clean_url": _normalize_url(url),
                "norm_title": re.sub(r"[^a-z0-9\s]", "", title.lower()).strip(),
                "tokens": _title_tokens(title),
            })
            unique.append(d)

    return unique


# ─── Feed Parsing Helpers ─────────────────────────────────────
def _fetch_rss(url: str, max_items: int = 15, default_source: str = "") -> List[Document]:
    """Parse an RSS feed and return LangChain Documents."""
    docs = []
    try:
        feed = feedparser.parse(url)
        feed_title = getattr(feed.feed, "title", default_source or "News Feed")

        for entry in feed.entries[:max_items]:
            raw_title = _clean(getattr(entry, "title", ""))
            summary = _clean(getattr(entry, "summary", ""))
            link = getattr(entry, "link", "")
            pub = getattr(entry, "published", "")

            if not raw_title:
                continue

            # Extract publisher if format is "Headline - Source"
            source = feed_title
            title = raw_title
            if " - " in raw_title:
                parts = raw_title.rsplit(" - ", 1)
                if len(parts[1].strip()) <= 45 and not parts[1].strip().isdigit():
                    title = parts[0].strip()
                    source = parts[1].strip()

            pub_dt = _parse_pub_date(pub)
            iso_date = pub_dt.isoformat() if pub_dt else ""
            time_ago = format_time_ago(pub_dt)
            rel_score = get_source_reliability(source)
            category = _detect_category(title, summary)

            # Clean up repetitive summary from RSS feeds that only mirror the headline
            clean_summary = summary
            if clean_summary:
                t_norm = re.sub(r"[^a-z0-9]", "", title.lower())
                s_norm = re.sub(r"[^a-z0-9]", "", clean_summary.lower())
                src_norm = re.sub(r"[^a-z0-9]", "", source.lower())
                if s_norm in (t_norm, t_norm + src_norm, src_norm + t_norm) or len(s_norm) <= len(t_norm) + 8:
                    clean_summary = f"Full report and verified dispatches from {source} on this unfolding development."

            content = f"Title: {title}\nSource: {source}\nPublished: {pub}\nSummary: {clean_summary}"
            docs.append(Document(
                page_content=content,
                metadata={
                    "title": title,
                    "url": link,
                    "source": source,
                    "date": pub,
                    "iso_date": iso_date,
                    "time_ago": time_ago,
                    "reliability_score": rel_score,
                    "category": category,
                    "summary": clean_summary or title,
                    "fetch_method": "rss",
                },
            ))
    except Exception as e:
        logger.warning(f"RSS fetch failed ({url}): {e}")
    return docs


def _fetch_google_news_rss(query: str, max_items: int = 20, gl: str = "IN") -> List[Document]:
    """Fetch from Google News RSS using topic query and country code."""
    country_code = gl.upper() if gl else "IN"
    hl = f"en-{country_code}"
    url = GOOGLE_NEWS_RSS.format(
        query=requests.utils.quote(query),
        hl=hl,
        gl=country_code,
        lang="en",
    )
    return _fetch_rss(url, max_items=max_items, default_source="Google News")


def _fetch_gnews_api(query: str, max_items: int = 10, country: str = "in") -> List[Document]:
    """Fetch from GNews API if key is present."""
    if not GNEWS_API_KEY:
        return []
    docs = []
    try:
        params = {
            "q": query,
            "lang": "en",
            "country": country.lower() if country else "in",
            "max": max_items,
            "apikey": GNEWS_API_KEY,
        }
        resp = requests.get(GNEWS_API_BASE_URL, params=params, timeout=8)
        data = resp.json()
        for art in data.get("articles", []):
            title = _clean(art.get("title", ""))
            desc = _clean(art.get("description", ""))
            content_text = _clean(art.get("content", desc))
            url = art.get("url", "")
            src = art.get("source", {}).get("name", "GNews")
            pub = art.get("publishedAt", "")

            if not title:
                continue

            pub_dt = _parse_pub_date(pub)
            iso_date = pub_dt.isoformat() if pub_dt else ""
            time_ago = format_time_ago(pub_dt)
            category = _detect_category(title, desc)
            rel_score = get_source_reliability(src)

            content = f"Title: {title}\nSource: {src}\nPublished: {pub}\nSummary: {desc}\n\n{content_text}"
            docs.append(Document(
                page_content=content,
                metadata={
                    "title": title,
                    "url": url,
                    "source": src,
                    "date": pub,
                    "iso_date": iso_date,
                    "time_ago": time_ago,
                    "reliability_score": rel_score,
                    "category": category,
                    "summary": desc or title,
                    "fetch_method": "gnews_api",
                },
            ))
    except Exception as e:
        logger.warning(f"GNews API failed: {e}")
    return docs


# ─── Public Fetch API ─────────────────────────────────────────
def fetch_news(topic: str = "latest news", hours: int = 48, country_code: str = "IN") -> List[Document]:
    """
    Fetch news articles for a given topic or query.
    Multi-source: Google News RSS + topic RSS feeds + GNews API.
    Deduplicated and tagged with metadata.
    """
    key = _cache_key(topic, country_code)
    if _is_fresh(key):
        logger.info(f"📦 Cache hit for '{topic}' ({len(_cache[key]['data'])} articles)")
        return _cache[key]["data"]

    docs: List[Document] = []

    # 1. Google News RSS search
    docs += _fetch_google_news_rss(topic, max_items=22, gl=country_code)

    # 2. GNews API if available
    if GNEWS_API_KEY:
        docs += _fetch_gnews_api(topic, max_items=8, country=country_code)

    # 3. Fallback to topic RSS feeds if needed
    if len(docs) < 8:
        # Match topic bucket
        t_low = topic.lower()
        matched_feed = None
        for cat_key in TOPIC_RSS_FEEDS:
            if cat_key in t_low:
                matched_feed = TOPIC_RSS_FEEDS[cat_key]
                break
        feeds_to_try = matched_feed or TOPIC_RSS_FEEDS["default"]
        for f_url in feeds_to_try:
            docs += _fetch_rss(f_url, max_items=6)
            if len(docs) >= 20:
                break

    # 4. Final safety fallback
    if len(docs) < 3:
        for f_url in TOPIC_RSS_FEEDS["default"]:
            docs += _fetch_rss(f_url, max_items=6)

    # Deduplicate
    unique = _deduplicate(docs)

    # Sort primarily by reliability and recency
    unique.sort(key=lambda d: (d.metadata.get("reliability_score", 0.6), d.metadata.get("iso_date", "")), reverse=True)

    logger.info(f"✅ Fetched {len(unique)} unique articles for topic '{topic}'")
    _cache[key] = {"data": unique, "ts": time.time()}
    return unique


def fetch_news_multi_query(queries: List[str], hours: int = 48, country_code: str = "IN") -> List[Document]:
    """Fetch and merge results from multiple query variations."""
    all_docs = []
    for q in queries:
        all_docs += fetch_news(q, hours=hours, country_code=country_code)
    return _deduplicate(all_docs)


def fetch_scoped_news(
    scope: str = "global",
    location: Optional[Dict[str, str]] = None,
    custom_query: Optional[str] = None,
) -> List[Document]:
    """
    Fetch news tailored to specific scopes:
      - 'local': Local city & state news (e.g. Kolkata / West Bengal, or city where user is located)
      - 'national': National news for user's country
      - 'global': Worldwide international headlines
    Does not restrict global discovery.
    """
    loc = location or {}
    city = loc.get("city", "").strip()
    region = loc.get("region", "").strip()
    country = loc.get("country", "India").strip()
    country_code = loc.get("country_code", "IN").strip() or "IN"

    if custom_query:
        return fetch_news(custom_query, country_code=country_code)

    if scope == "local":
        if city and city.lower() != "unknown":
            q = f"{city} {region} news OR {city} local updates" if region else f"{city} local news"
        elif region and region.lower() != "unknown":
            q = f"{region} news updates"
        else:
            q = f"{country} local news"
        docs = fetch_news(q, country_code=country_code)
        for d in docs:
            d.metadata["scope"] = "Local"
            d.metadata["location_tag"] = city if city and city.lower() != "unknown" else region
        return docs

    elif scope == "national":
        q = f"{country} national news headlines"
        docs = fetch_news(q, country_code=country_code)
        for d in docs:
            d.metadata["scope"] = "National"
            d.metadata["location_tag"] = country
        return docs

    else:  # global
        q = "world news international headlines diplomacy"
        docs = fetch_news(q, country_code="US")  # global bias
        for d in docs:
            d.metadata["scope"] = "Global"
            d.metadata["location_tag"] = "Global"
        return docs


def clear_cache():
    """Clear in-memory cache."""
    _cache.clear()
    logger.info("🗑 News cache cleared")


def get_available_topics() -> List[str]:
    return [
        "Technology & AI",
        "Markets & Economy",
        "Politics & Policy",
        "Science & Climate",
        "Health & Medicine",
        "Sports",
        "World Affairs",
    ]
