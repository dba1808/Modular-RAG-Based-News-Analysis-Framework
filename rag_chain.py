"""
RAG Chain Module — Advanced Edition
────────────────────────────────────
Builds the RetrievalQA chain with:
  • Multi-query generation
  • Cross-encoder reranking
  • Structured fact extraction
  • Knowledge graph generation
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from llm_factory import get_llm
from config import (
    SYSTEM_PROMPT,
    OPENROUTER_MODEL,
    TEMPERATURE,
    MULTI_QUERY_COUNT,
    RERANKER_MODEL,
    RERANK_TOP_K,
)

logger = logging.getLogger("news_rag.rag_chain")

# ─── Prompt Template ────────────────────────────────────────
_PROMPT_TEMPLATE = """{system_prompt}

--- RETRIEVED NEWS CONTEXT ---
{context}

--- USER QUESTION ---
{question}

Provide a structured, professional answer based ONLY on the news context above.
If the context doesn't have enough information, say: "Not enough recent information found."
"""

QA_PROMPT = PromptTemplate(
    template=_PROMPT_TEMPLATE,
    input_variables=["context", "question"],
    partial_variables={"system_prompt": SYSTEM_PROMPT},
)


# ─── Multi-Query Generation ─────────────────────────────────
def generate_multi_queries(llm, original_query: str, num_queries: int = MULTI_QUERY_COUNT) -> List[str]:
    """
    Generate alternative search queries using the LLM.
    This helps retrieve documents that a single query might miss.
    """
    prompt = f"""Generate {num_queries} alternative search queries for this news search query.
Each query should approach the topic from a different angle to maximize relevant results.
Return ONLY the queries, one per line. No numbering, no explanation.

Original query: "{original_query}"
"""
    try:
        response = llm.invoke([
            SystemMessage(content="You are a search query optimization assistant."),
            HumanMessage(content=prompt),
        ])
        queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        # Always include the original
        all_queries = [original_query] + queries[:num_queries]
        logger.info(f"🔀 Multi-query: {len(all_queries)} queries generated")
        return all_queries
    except Exception as e:
        logger.warning(f"Multi-query generation failed: {e}")
        return [original_query]


# ─── Cross-Encoder Reranking ────────────────────────────────
_reranker = None


def _get_reranker():
    """Load the cross-encoder reranker model (cached)."""
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(RERANKER_MODEL)
            logger.info(f"✅ Reranker loaded: {RERANKER_MODEL}")
        except ImportError:
            logger.warning("sentence-transformers not available — reranking disabled")
        except Exception as e:
            logger.warning(f"Reranker load failed: {e}")
    return _reranker


def rerank_documents(
    query: str,
    documents: List[Tuple[Document, float]],
    top_k: int = RERANK_TOP_K,
) -> List[Tuple[Document, float]]:
    """
    Re-rank documents using a cross-encoder for better relevance.
    Input: list of (Document, score) tuples from hybrid search.
    """
    reranker = _get_reranker()
    if not reranker or not documents:
        return documents[:top_k]

    try:
        pairs = [(query, doc.page_content[:512]) for doc, _ in documents]
        scores = reranker.predict(pairs)
        reranked = list(zip([d for d, _ in documents], scores))
        reranked.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"🏆 Reranked {len(documents)} → top {top_k}")
        return reranked[:top_k]
    except Exception as e:
        logger.warning(f"Reranking failed: {e}")
        return documents[:top_k]


# ─── Structured Fact Extraction ─────────────────────────────
def extract_facts(llm, text: str) -> List[Dict[str, str]]:
    """Extract structured facts from article text using the LLM."""
    prompt = """Extract key structured facts from this news content.
Return as a list of facts, each with these fields:
- Entity: (company, person, country, etc.)
- Event: (what happened)
- Detail: (specific numbers, dates, amounts)
- Date: (when, if mentioned)

Format each fact on one line as: Entity | Event | Detail | Date

NEWS CONTENT:
""" + text[:3000]

    try:
        response = llm.invoke([
            SystemMessage(content="You extract structured facts from news articles. Be concise and accurate."),
            HumanMessage(content=prompt),
        ])
        facts = []
        for line in response.content.strip().split("\n"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                facts.append({
                    "entity": parts[0],
                    "event": parts[1],
                    "detail": parts[2],
                    "date": parts[3] if len(parts) > 3 else "",
                })
        return facts
    except Exception as e:
        logger.warning(f"Fact extraction failed: {e}")
        return []


# ─── Knowledge Graph Generation ─────────────────────────────
def generate_knowledge_graph(llm, text: str) -> List[Dict[str, str]]:
    """Generate entity-relationship triples from news content."""
    prompt = """Extract entity relationships from this news content.
Return as relationship triples, one per line:
Subject | Relationship | Object

Example:
Nvidia | reported revenue | $18B
US | imposed sanctions on | China

NEWS CONTENT:
""" + text[:3000]

    try:
        response = llm.invoke([
            SystemMessage(content="You extract entity relationships from news articles."),
            HumanMessage(content=prompt),
        ])
        triples = []
        for line in response.content.strip().split("\n"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                triples.append({
                    "subject": parts[0],
                    "relationship": parts[1],
                    "object": parts[2],
                })
        return triples
    except Exception as e:
        logger.warning(f"Knowledge graph generation failed: {e}")
        return []


# ─── Build RAG chain (backwards compatible) ─────────────────
def build_rag_chain(llm, retriever) -> RetrievalQA:
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_PROMPT},
    )
    logger.info("🔗 RAG chain built")
    return chain


def run_query(chain: RetrievalQA, question: str) -> dict:
    try:
        response = chain.invoke({"query": question})
        return {
            "result": response.get("result", "No response generated."),
            "source_documents": response.get("source_documents", []),
        }
    except Exception as e:
        logger.error(f"💥 Query failed: {e}")
        return {
            "result": f"Error: {str(e)}",
            "source_documents": [],
        }
