# Modular RAG-Based News Analysis Framework

A real-time, dual-LLM powered News Intelligence system built using LangChain, Gemini, Ollama, FAISS, and Streamlit.

This project implements a production-style Retrieval-Augmented Generation (RAG) pipeline that fetches live news data, converts it into vector embeddings, stores it in a FAISS vector database, retrieves relevant context based on user queries, and generates structured responses using either Gemini (cloud) or Ollama (local) models. The system includes automatic fallback logic, similarity-based filtering, modular architecture, secure environment configuration using `.env`, and a clean Streamlit UI. 

It demonstrates practical system design including real-time data ingestion, semantic search, LLM abstraction, dual-model orchestration, and scalable backend structuring — focusing on real-world AI architecture rather than simple prompt engineering.

Tech Stack: Python, LangChain, Gemini API, Ollama, FAISS, Streamlit, python-dotenv.

Run locally:
1. Create virtual environment  
2. Install dependencies (`pip install -r requirements.txt`)  
3. Add `.env` file with API keys  
4. Run `streamlit run app.py`
