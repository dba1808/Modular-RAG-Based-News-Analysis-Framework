"""
LLM Factory Module — Gemini Only
─────────────────────────────────
Uses the new google-genai SDK via langchain-google-genai 2.x
which calls the v1 API (not deprecated v1beta).
"""

import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE

logger = logging.getLogger("news_rag.llm_factory")


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Create and return the Gemini LLM instance.
    Raises RuntimeError if API key is not configured.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please add it to your .env file.\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )

    # Set env var — langchain-google-genai 2.x picks this up automatically
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=TEMPERATURE,
        )
        logger.info(f"✅ Gemini LLM ready ({GEMINI_MODEL})")
        return llm
    except Exception as e:
        logger.error(f"💥 Failed to initialise Gemini: {e}")
        raise RuntimeError(f"Could not start Gemini: {e}")


def check_status() -> dict:
    """Return Gemini availability status."""
    ok = bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key_here")
    return {
        "available": ok,
        "model": GEMINI_MODEL,
        "status": "✅ Ready" if ok else "❌ API key not set",
    }
