"""
Configuration module for the News RAG system.
Loads environment variables and provides centralized config.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── API Keys ───────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# langchain-google-genai 2.x uses GOOGLE_API_KEY env var to hit the v1 API
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# ─── Model Configuration ────────────────────────────────────
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMBEDDING_MODEL = "models/text-embedding-004"
TEMPERATURE = 0.3

# ─── FAISS Configuration ────────────────────────────────────
FAISS_INDEX_PATH = "faiss_index"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 5
SIMILARITY_THRESHOLD = 0.3

# ─── News API Configuration ─────────────────────────────────
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"
NEWS_PAGE_SIZE = 20
NEWS_CACHE_TTL_SECONDS = 900  # 15 minutes

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

### 📰 Summary
Brief overview of what's happening.

### 🔍 Key Developments
- Bullet points of the main facts

### 📊 Impact Analysis
Why this matters and what it means.

### 🌡 Sentiment
Overall tone: Positive / Neutral / Negative

### 📌 Sources
List the source names from the context.
"""
