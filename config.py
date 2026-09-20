"""
Configuration module for the News Intelligence Platform.
Loads environment variables and provides centralized config.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Application Branding ────────────────────────────────────
APP_NAME_BN = "ত্রিকোণদৃষ্টি"
APP_NAME_EN = "TrikonDrishti"
APP_TAGLINE = "Multi-Dimensional News Intelligence Platform"

# ─── API Keys & Endpoints ────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# ─── Model Configuration ────────────────────────────────────
# Default strong model available on OpenRouter; easily configurable via .env
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
AVAILABLE_MODELS = [
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.3-70b-instruct",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-mini",
    "deepseek/deepseek-chat",
    "mistralai/mistral-large-2411",
]
TEMPERATURE = 0.3

# ─── FAISS Configuration ────────────────────────────────────
FAISS_INDEX_PATH = "faiss_index"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 10          # Retrieve more for reranking
SIMILARITY_THRESHOLD = 0.25 # Slightly wider net for hybrid

# ─── BM25 / Hybrid Retrieval ────────────────────────────────
BM25_WEIGHT = 0.35           # Weight for keyword search
VECTOR_WEIGHT = 0.65         # Weight for semantic search
HYBRID_TOP_K = 10            # Candidates for reranking

# ─── Cross-Encoder Reranking ────────────────────────────────
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANK_TOP_K = 5             # Final docs after reranking

# ─── Multi-Query ────────────────────────────────────────────
MULTI_QUERY_COUNT = 3        # Number of alternative queries

# ─── Time Decay ─────────────────────────────────────────────
TIME_DECAY_FACTOR = 0.15     # Higher = stronger recency bias
TIME_DECAY_HALFLIFE_HOURS = 12

# ─── Source Reliability ─────────────────────────────────────
SOURCE_RELIABILITY_SCORES = {
    # Tier 1 – Very High (0.95 – 1.0)
    "reuters": 1.0,
    "associated press": 0.98,
    "bbc news": 0.95,
    "bbc": 0.95,
    "the new york times": 0.95,
    "nytimes": 0.95,
    # Tier 2 – High (0.85 – 0.94)
    "the guardian": 0.92,
    "the washington post": 0.91,
    "al jazeera": 0.90,
    "bloomberg": 0.93,
    "financial times": 0.93,
    "the economist": 0.92,
    "wired": 0.88,
    "techcrunch": 0.88,
    "ars technica": 0.88,
    "espn": 0.87,
    "espncricinfo": 0.87,
    # Tier 3 – Medium (0.70 – 0.84)
    "cnn": 0.82,
    "cnbc": 0.82,
    "fox news": 0.75,
    "the hindu": 0.80,
    "times of india": 0.78,
    "ndtv": 0.80,
    "india today": 0.78,
    "hindustan times": 0.78,
    "the verge": 0.82,
    "engadget": 0.80,
    "mashable": 0.76,
    # Tier 4 – Lower (0.50 – 0.69)
    "buzzfeed": 0.55,
    "daily mail": 0.50,
    # Default
    "default": 0.60,
}

# ─── News Ingestion ─────────────────────────────────────────
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"
GNEWS_API_BASE_URL = "https://gnews.io/api/v4/search"
NEWS_PAGE_SIZE = 20
NEWS_CACHE_TTL_SECONDS = 900  # 15 minutes

# ─── Topic Clustering ───────────────────────────────────────
CLUSTER_MIN_ARTICLES = 2
CLUSTER_MAX_TOPICS = 8
CLUSTER_SIMILARITY_THRESHOLD = 0.45

# ─── Sentiment ──────────────────────────────────────────────
SENTIMENT_LABELS = ["positive", "negative", "neutral"]

# ─── Scheduler ──────────────────────────────────────────────
AUTO_REFRESH_INTERVAL_MINUTES = 60  # Re-index hourly

# ─── Logging ────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_LEVEL = logging.INFO

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger("news_rag")

# ─── System Prompt ──────────────────────────────────────────
SYSTEM_PROMPT = """You are a professional News Intelligence Assistant.

Rules:
1. Answer strictly based on retrieved context.
2. Do not hallucinate.
3. If insufficient data, say: "Not enough recent information found."

Structure your response as:

### Executive Summary
Brief overview of what's happening.

### Key Developments
- Bullet points of the main facts

### Impact Analysis
Why this matters and what it means.

### Strategic Sentiment
Overall tone: Positive / Neutral / Negative

### Sources
List the source names from the context.
"""

