"""
LLM Factory Module — OpenRouter Integration
─────────────────────────────────────────────
Modular AI layer connecting to OpenRouter API (OpenAI-compatible).
Supports dynamic model switching, fallback handling, and custom headers.
"""

import os
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    AVAILABLE_MODELS,
    TEMPERATURE,
    APP_NAME_BN,
    APP_NAME_EN,
)

logger = logging.getLogger("news_rag.llm_factory")

# Global LLM instance cache by (model, temperature)
_llm_cache: Dict[str, ChatOpenAI] = {}


def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = 500,
    max_retries: int = 2,
    timeout: int = 45,
) -> ChatOpenAI:
    """
    Create and return an OpenRouter ChatOpenAI instance.
    Raises RuntimeError if OPENROUTER_API_KEY is missing or invalid.
    """
    api_key = os.getenv("OPENROUTER_API_KEY") or OPENROUTER_API_KEY
    if not api_key or api_key.strip() in ("", "your_key_here", "your_openrouter_key_here"):
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Please add it to your .env file as:\n"
            "OPENROUTER_API_KEY=your_key_here\n\n"
            "Get an OpenRouter key at: https://openrouter.ai/keys"
        )

    selected_model = model or os.getenv("OPENROUTER_MODEL") or OPENROUTER_MODEL
    selected_temp = temperature if temperature is not None else TEMPERATURE
    cache_key = f"{selected_model}:{selected_temp}:{max_tokens}"

    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    headers = {
        "HTTP-Referer": "https://trikondrishti.news",
        "X-Title": f"{APP_NAME_EN} News Intelligence",
    }

    try:
        llm = ChatOpenAI(
            model=selected_model,
            openai_api_key=api_key,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=selected_temp,
            max_tokens=max_tokens,
            max_retries=max_retries,
            request_timeout=timeout,
            default_headers=headers,
        )
        _llm_cache[cache_key] = llm
        logger.info(f"✅ OpenRouter LLM initialized ({selected_model})")
        return llm
    except Exception as e:
        logger.error(f"💥 Failed to initialize OpenRouter LLM ({selected_model}): {e}")
        raise RuntimeError(f"Could not connect to OpenRouter with model '{selected_model}': {e}")


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = 500,
) -> str:
    """Convenience helper to invoke the OpenRouter LLM with system + user messages."""
    llm = get_llm(model=model, temperature=temperature, max_tokens=max_tokens)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


def check_status(model: Optional[str] = None) -> dict:
    """Return OpenRouter availability status and active model."""
    api_key = os.getenv("OPENROUTER_API_KEY") or OPENROUTER_API_KEY
    active_model = model or os.getenv("OPENROUTER_MODEL") or OPENROUTER_MODEL
    has_key = bool(api_key and api_key.strip() not in ("", "your_key_here", "your_openrouter_key_here"))

    return {
        "available": has_key,
        "provider": "OpenRouter",
        "model": active_model,
        "available_models": AVAILABLE_MODELS,
        "status": "Ready (OpenRouter)" if has_key else "OPENROUTER_API_KEY not set in .env",
    }


if __name__ == "__main__":
    import sys
    # Ensure UTF-8 output encoding on Windows consoles
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 50)
    print("Testing LLM Factory Connection...")
    print("=" * 50)
    status = check_status()
    print(f"Status   : {status['status']}")
    print(f"Provider : {status['provider']}")
    print(f"Model    : {status['model']}")
    print(f"Available: {status['available']}")

    if status["available"]:
        print("\nSending a quick test query to OpenRouter...")
        try:
            test_reply = call_llm(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'TrikonDrishti LLM is online!' in 5 words or less.",
            )
            print(f"Response : {test_reply.strip()}")
            print("\nLLM Factory is working successfully!")
        except Exception as err:
            print(f"Connection test failed: {err}")
    else:
        print("\nPlease configure OPENROUTER_API_KEY in your .env file to enable live LLM queries.")

