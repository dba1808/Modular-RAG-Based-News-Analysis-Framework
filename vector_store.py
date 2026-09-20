"""
Vector Store Module — Hybrid Retrieval Edition
───────────────────────────────────────────────
Manages FAISS vector store with:
  • Semantic (embedding) search
  • BM25 keyword search
  • Hybrid scoring (weighted combination)
  • Time-decay relevance weighting
  • Source reliability boosting
"""

import os
import re
import math
import shutil
import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    FAISS_INDEX_PATH,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K,
    SIMILARITY_THRESHOLD,
    BM25_WEIGHT,
    VECTOR_WEIGHT,
    TIME_DECAY_FACTOR,
    TIME_DECAY_HALFLIFE_HOURS,
    SOURCE_RELIABILITY_SCORES,
)

logger = logging.getLogger("news_rag.vector_store")

# ─── Embedding model cache ───────────────────────────────────
_embeddings_instance = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Load free local HuggingFace embeddings (all-MiniLM-L6-v2)."""
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info("Loading HuggingFace embedding model ...")
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("✅ Embedding model loaded")
    return _embeddings_instance


# ─── BM25 keyword search ────────────────────────────────────
class BM25Index:
    """Lightweight BM25 index over document chunks."""

    def __init__(self):
        self.documents: List[Document] = []
        self.corpus: List[List[str]] = []
        self.bm25 = None

    def build(self, documents: List[Document]):
        self.documents = documents
        self.corpus = [self._tokenize(d.page_content) for d in documents]
        if self.corpus:
            try:
                from rank_bm25 import BM25Okapi
                self.bm25 = BM25Okapi(self.corpus)
            except ImportError:
                logger.warning("rank_bm25 not installed — BM25 disabled")
                self.bm25 = None

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        if not self.bm25 or not self.documents:
            return []
        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)
        max_score = max(scores) if max(scores) > 0 else 1.0
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in ranked[:top_k]:
            normalized = score / max_score  # Normalize to 0-1
            results.append((self.documents[idx], normalized))
        return results

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.sub(r"[^a-z0-9\s]", "", text.lower()).split()


# Global BM25 index
_bm25_index = BM25Index()


# ─── Document chunking ──────────────────────────────────────
def chunk_documents(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"✂️  Split {len(documents)} docs → {len(chunks)} chunks")
    return chunks


# ─── Build / Load / Update FAISS ─────────────────────────────
def build_vector_store(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> FAISS:
    if not documents:
        raise ValueError("No documents provided to build vector store")

    embeddings = _get_embeddings()
    chunks = chunk_documents(documents, chunk_size, chunk_overlap)

    logger.info(f"🔨 Building FAISS index with {len(chunks)} chunks …")
    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(FAISS_INDEX_PATH)

    # Build BM25 index in parallel
    _bm25_index.build(chunks)

    logger.info(f"💾 FAISS + BM25 index built")
    return store


def load_vector_store() -> Optional[FAISS]:
    if not os.path.exists(FAISS_INDEX_PATH):
        logger.info("📂 No existing FAISS index found")
        return None
    try:
        embeddings = _get_embeddings()
        store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info("✅ FAISS index loaded from disk")
        return store
    except Exception as e:
        logger.error(f"💥 Error loading FAISS index: {e}")
        return None


def update_vector_store(
    new_documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> FAISS:
    embeddings = _get_embeddings()
    chunks = chunk_documents(new_documents, chunk_size, chunk_overlap)

    existing = load_vector_store()
    if existing is not None:
        logger.info(f"➕ Adding {len(chunks)} new chunks to existing index")
        existing.add_documents(chunks)
        existing.save_local(FAISS_INDEX_PATH)
        _bm25_index.build(chunks)  # Rebuild BM25 with new docs
        return existing
    else:
        return build_vector_store(new_documents, chunk_size, chunk_overlap)


# ─── Time Decay Scoring ─────────────────────────────────────
def _compute_time_decay(doc: Document) -> float:
    """Compute a recency boost factor (0 to 1). Newer = higher."""
    date_str = doc.metadata.get("iso_date", "") or doc.metadata.get("date", "")
    if not date_str:
        return 0.5  # Unknown date → neutral

    try:
        if isinstance(date_str, str):
            # Try ISO format
            pub_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            return 0.5
    except (ValueError, TypeError):
        return 0.5

    now = datetime.now(timezone.utc)
    try:
        if pub_dt.tzinfo is None:
            from datetime import timezone as tz
            pub_dt = pub_dt.replace(tzinfo=tz.utc)
        hours_ago = (now - pub_dt).total_seconds() / 3600
    except Exception:
        return 0.5

    # Exponential decay
    decay = math.exp(-TIME_DECAY_FACTOR * hours_ago / TIME_DECAY_HALFLIFE_HOURS)
    return max(0.0, min(1.0, decay))


# ─── Source Reliability Scoring ──────────────────────────────
def _compute_source_score(doc: Document) -> float:
    """Get reliability score for the document's source."""
    source = doc.metadata.get("source", "").lower().strip()
    for name, score in SOURCE_RELIABILITY_SCORES.items():
        if name in source or source in name:
            return score
    return SOURCE_RELIABILITY_SCORES.get("default", 0.6)


# ─── Hybrid Retrieval ───────────────────────────────────────
def hybrid_search(
    store: FAISS,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    use_time_decay: bool = True,
    use_source_reliability: bool = True,
) -> List[Tuple[Document, float]]:
    """
    Perform hybrid search combining:
      1. FAISS vector similarity
      2. BM25 keyword matching
      3. Time-decay boosting
      4. Source reliability weighting
    """
    # 1. Vector search
    vector_results = store.similarity_search_with_score(query, k=top_k * 2)
    # FAISS returns L2 distance — lower is better. Convert to similarity 0-1.
    max_dist = max(d for _, d in vector_results) if vector_results else 1.0
    vector_scored: Dict[str, Tuple[Document, float]] = {}
    for doc, dist in vector_results:
        doc_id = doc.metadata.get("title", doc.page_content[:50])
        similarity = 1.0 - (dist / (max_dist + 1e-6))  # Normalize
        vector_scored[doc_id] = (doc, max(0, similarity))

    # 2. BM25 search
    bm25_results = _bm25_index.search(query, top_k=top_k * 2)
    bm25_scored: Dict[str, Tuple[Document, float]] = {}
    for doc, score in bm25_results:
        doc_id = doc.metadata.get("title", doc.page_content[:50])
        bm25_scored[doc_id] = (doc, score)

    # 3. Combine scores
    all_doc_ids = set(list(vector_scored.keys()) + list(bm25_scored.keys()))
    combined: List[Tuple[Document, float]] = []

    for doc_id in all_doc_ids:
        vec_score = vector_scored.get(doc_id, (None, 0.0))[1]
        bm_score = bm25_scored.get(doc_id, (None, 0.0))[1]
        doc = vector_scored.get(doc_id, bm25_scored.get(doc_id))[0]

        # Weighted hybrid score
        hybrid_score = (VECTOR_WEIGHT * vec_score) + (BM25_WEIGHT * bm_score)

        # Time decay boost
        if use_time_decay:
            time_boost = _compute_time_decay(doc)
            hybrid_score = hybrid_score * 0.75 + time_boost * 0.25

        # Source reliability boost
        if use_source_reliability:
            src_score = _compute_source_score(doc)
            hybrid_score = hybrid_score * 0.85 + src_score * 0.15

        combined.append((doc, hybrid_score))

    # Sort by final score
    combined.sort(key=lambda x: x[1], reverse=True)
    return combined[:top_k]


# ─── Standard retriever (backwards compatible) ──────────────
def get_retriever(store: FAISS, top_k: int = DEFAULT_TOP_K):
    retriever = store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": top_k,
            "score_threshold": SIMILARITY_THRESHOLD,
        },
    )
    return retriever


def similarity_search_with_scores(
    store: FAISS, query: str, top_k: int = DEFAULT_TOP_K
) -> List[Tuple[Document, float]]:
    results = store.similarity_search_with_score(query, k=top_k)
    return results


def clear_vector_store():
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)
        logger.info("🗑  FAISS index deleted")
    else:
        logger.info("📂 No FAISS index to delete")
