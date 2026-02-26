"""
RAG Chain Module
────────────────
Builds the RetrievalQA chain with a structured system prompt
and conversation memory.
"""

import logging
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

from config import SYSTEM_PROMPT

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

def build_rag_chain(llm, retriever) -> RetrievalQA:
    """Build a RetrievalQA chain with the given LLM and retriever."""
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": QA_PROMPT,
        },
    )
    logger.info("🔗 RAG chain built")
    return chain


def run_query(chain: RetrievalQA, question: str) -> dict:
    """Execute a query through the RAG chain."""
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
