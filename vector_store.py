"""
Vector Store Module
───────────────────
Manages FAISS vector store: embedding, indexing, incremental
updates, and retriever creation.
Embeddings: Free local HuggingFace sentence-transformers (no API key needed).
"""

import os
import shutil
import logging
from typing import List, Optional, Tuple

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    FAISS_INDEX_PATH,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K,
    SIMILARITY_THRESHOLD,
)

logger = logging.getLogger("news_rag.vector_store")


# Cache the embedding model so it's only loaded once
_embeddings_instance = None

def _get_embeddings() -> HuggingFaceEmbeddings:
    """Load free local HuggingFace embeddings (all-MiniLM-L6-v2)."""
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info("Loading HuggingFace embedding model (first run may take a moment)...")
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("✅ Embedding model loaded")
    return _embeddings_instance


def chunk_documents(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Document]:
    """
    Split documents into smaller chunks for embedding.

    Args:
        documents:     List of LangChain Documents.
        chunk_size:    Max characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of chunked Documents.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"✂️  Split {len(documents)} docs → {len(chunks)} chunks (size={chunk_size})")
    return chunks


def build_vector_store(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> FAISS:
    """
    Build a new FAISS vector store from documents.

    Args:
        documents:     Raw LangChain Documents.
        chunk_size:    Chunk size for splitting.
        chunk_overlap: Overlap size.

    Returns:
        FAISS vector store instance.
    """
    if not documents:
        raise ValueError("No documents provided to build vector store")

    embeddings = _get_embeddings()
    chunks = chunk_documents(documents, chunk_size, chunk_overlap)

    logger.info(f"🔨 Building FAISS index with {len(chunks)} chunks …")
    store = FAISS.from_documents(chunks, embeddings)

    # Persist to disk
    store.save_local(FAISS_INDEX_PATH)
    logger.info(f"💾 FAISS index saved to '{FAISS_INDEX_PATH}'")
    return store


def load_vector_store() -> Optional[FAISS]:
    """Load an existing FAISS index from disk."""
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
    """
    Incrementally update the FAISS index with new documents.
    If no existing index, builds from scratch.
    """
    embeddings = _get_embeddings()
    chunks = chunk_documents(new_documents, chunk_size, chunk_overlap)

    existing = load_vector_store()
    if existing is not None:
        logger.info(f"➕ Adding {len(chunks)} new chunks to existing index")
        existing.add_documents(chunks)
        existing.save_local(FAISS_INDEX_PATH)
        return existing
    else:
        return build_vector_store(new_documents, chunk_size, chunk_overlap)


def get_retriever(store: FAISS, top_k: int = DEFAULT_TOP_K):
    """
    Create a retriever from the FAISS store with similarity
    score threshold filtering.
    """
    retriever = store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": top_k,
            "score_threshold": SIMILARITY_THRESHOLD,
        },
    )
    logger.info(f"🔍 Retriever ready (top_k={top_k}, threshold={SIMILARITY_THRESHOLD})")
    return retriever


def similarity_search_with_scores(
    store: FAISS, query: str, top_k: int = DEFAULT_TOP_K
) -> List[Tuple[Document, float]]:
    """
    Run similarity search and return documents with their scores.
    """
    results = store.similarity_search_with_score(query, k=top_k)
    logger.info(f"🎯 Found {len(results)} results for query")
    return results


def clear_vector_store():
    """Delete the persisted FAISS index."""
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)
        logger.info("🗑  FAISS index deleted")
    else:
        logger.info("📂 No FAISS index to delete")
