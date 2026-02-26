"""
📰 News Intelligence — Polished Professional UI
"""

import os
import base64
import time
import streamlit as st
import requests as _requests

st.set_page_config(
    page_title="News Intelligence",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from news_fetcher import fetch_news
from config import GEMINI_API_KEY, GEMINI_MODEL

os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY or ""

def call_gemini(sys_p: str, usr_p: str) -> str:
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.3)
    resp = llm.invoke([SystemMessage(content=sys_p), HumanMessage(content=usr_p)])
    return resp.content

SYS_PROMPT = """You are an expert News Analyst AI. Provide detailed, well-organized news briefings.

IMPORTANT FORMATTING RULES:
- Do NOT use any markdown headers (no # or ## or ###).
- Use **bold labels** for section names insteadin fancy and colored and better font way .
- Use tables where possible for structured data.
- Write in clean paragraphs and bullet points if needed .

Structure your response EXACTLY like this:

**📰 What Happened**
Write a clear 3-4 sentence overview explaining the full situation. Cover who, what, where, when.

**🔍 Key Facts**

| # | Detail |
|---|--------|
| 1 | First key fact |
| 2 | Second key fact |
| 3 | Third key fact |
| 4 | Fourth key fact |
| 5 | Fifth key fact |

**🌍 Background**
2-3 sentences explaining the broader context. Why is this happening now? What led to this? Any past news related to this ? 

**📊 Impact**

| Who is Affected | How |
|----------------|-----|
| Group 1 | Impact description |
| Group 2 | Impact description |

**🌡️ Sentiment:** Positive / Neutral / Negative — one sentence explaining why.

**📌 Sources:** List source names separated by commas.

Be thorough and detailed. Give a COMPLETE picture. The user wants a full news briefing, not a short summary."""


# ─── Background ──────────────────────────────────────────────
def load_bg():
    p = os.path.join(os.path.dirname(__file__), "room_bg.png")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

bg64 = load_bg()


# ─── CSS ─────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Playfair+Display:wght@600;700&display=swap');

:root {{
    --bg: #f2f1ec;
    --card: rgba(255,255,255,0.88);
    --card-hover: rgba(255,255,255,0.95);
    --border: rgba(0,0,0,0.06);
    --text: #1a1a1a;
    --text-mid: #444;
    --text-soft: #777;
    --text-muted: #aaa;
    --accent: #2d2d2d;
    --radius: 18px;
}}

html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; -webkit-font-smoothing: antialiased; }}
#MainMenu, footer, header {{ visibility: hidden; }}

.stApp {{
    background-color: var(--bg);
    {"background-image: url('data:image/png;base64," + bg64 + "');" if bg64 else ""}
    background-size: cover; background-position: center; background-attachment: fixed;
}}
.stApp::before {{
    content: ""; position: fixed; inset: 0;
    background: rgba(242,241,236,0.6);
    backdrop-filter: blur(3px); z-index: 0; pointer-events: none;
}}
.block-container {{
    position: relative; z-index: 1;
    padding: 0 !important; max-width: 100% !important;
}}

/* ── Sidebar ────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: var(--card) !important;
    backdrop-filter: blur(28px) !important;
    border-right: 1px solid var(--border) !important;
}}
.sb-head {{
    padding: 1.5rem 1.4rem 1.1rem;
    border-bottom: 1px solid var(--border);
}}
.sb-head h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem; color: var(--text); margin: 0;
}}
.sb-head p {{
    color: var(--text-muted); font-size: 0.66rem; margin: 4px 0 0;
    text-transform: uppercase; letter-spacing: 2px;
}}
.sb-label {{
    color: var(--text-muted); font-size: 0.62rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    padding: 1.2rem 1.4rem 0.4rem;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background: rgba(0,0,0,0.025) !important;
    color: var(--text) !important;
    border: 1px solid rgba(0,0,0,0.06) !important;
    border-radius: 12px !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    text-align: left !important; padding: 0.55rem 1rem !important;
    transition: all 0.15s !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(0,0,0,0.055) !important;
    transform: translateX(2px) !important;
}}

/* ── Chat area ──────────────────────────── */
.chat-area {{
    max-width: 760px; margin: 0 auto;
    padding: 1rem 1rem 7rem;
}}

/* ── Greeting ────────────────────────────── */
.greeting {{
    text-align: center; padding: 5rem 1rem 2rem;
    animation: slideUp 0.5s ease-out;
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(24px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.g-icon {{
    width: 64px; height: 64px;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 18px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.7rem; margin-bottom: 1.2rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}}
.greeting h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem; color: var(--text); margin: 0; font-weight: 700;
    letter-spacing: -0.3px;
}}
.greeting p {{
    color: var(--text-soft); font-size: 0.92rem; margin: 8px 0 0;
}}
.greeting .hint {{
    color: var(--text-muted); font-size: 0.78rem; margin-top: 2rem;
    font-style: italic;
}}

/* ── Messages ────────────────────────────── */
.msg {{
    display: flex; gap: 14px; margin-bottom: 20px;
    align-items: flex-start; animation: slideUp 0.3s ease-out;
}}
.msg.user {{ justify-content: flex-end; }}

.av {{
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; flex-shrink: 0;
}}
.av-u {{ background: #e5e4df; }}
.av-a {{ background: var(--accent); color: #fff; font-size: 0.85rem; }}

/* User bubble */
.bub-u {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 20px 20px 6px 20px;
    padding: 14px 20px; font-size: 0.9rem; line-height: 1.6;
    max-width: 70%; color: var(--text);
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}}

/* AI answer card — the main redesign */
.answer-card {{
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 0;
    max-width: 92%;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    overflow: hidden;
}}
.answer-header {{
    background: linear-gradient(135deg, #2d2d2d, #3d3d3d);
    padding: 14px 22px;
    display: flex; align-items: center; gap: 10px;
}}
.answer-header span {{
    color: #fff; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.5px;
}}
.answer-body {{
    padding: 22px 26px 24px;
}}

/* Section blocks inside answer */
.section-block {{
    margin-bottom: 20px;
    padding-bottom: 18px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
}}
.section-block:last-child {{
    border-bottom: none; margin-bottom: 0; padding-bottom: 0;
}}
.section-icon {{
    font-size: 1.2rem;
    margin-right: 6px;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700;
    color: var(--text); margin: 0 0 8px;
}}
.section-text {{
    font-size: 0.88rem; line-height: 1.78;
    color: var(--text-mid);
}}
.section-text ul {{
    margin: 6px 0; padding-left: 1.2rem;
}}
.section-text li {{
    margin-bottom: 6px;
    padding-left: 4px;
}}
.section-text li::marker {{
    color: var(--text-muted);
}}
.section-text strong {{
    color: var(--text);
}}

/* Sentiment tag */
.sentiment-tag {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}}
.sent-pos {{ background: #e6f9e6; color: #2d7a2d; }}
.sent-neg {{ background: #fce8e8; color: #a33; }}
.sent-neu {{ background: #f0f0ea; color: #666; }}

/* ── Sources ─────────────────────────────── */
.src-card {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    background: rgba(0,0,0,0.015);
    border: 1px solid var(--border);
    border-radius: 12px; margin: 5px 0;
    transition: all 0.15s;
}}
.src-card:hover {{
    background: rgba(0,0,0,0.03);
    transform: translateX(3px);
}}
.src-dot {{
    width: 6px; height: 6px;
    background: var(--text-muted);
    border-radius: 50%; flex-shrink: 0;
}}
.src-name {{ font-size: 0.78rem; color: var(--text-soft); font-weight: 600; }}
.src-link {{ font-size: 0.78rem; }}
.src-link a {{ color: var(--text-mid); text-decoration: none; }}
.src-link a:hover {{ text-decoration: underline; color: var(--text); }}

/* ── Chat input ──────────────────────────── */
[data-testid="stChatInput"] {{
    background: var(--card) !important;
    border: 1.5px solid rgba(0,0,0,0.09) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(24px) !important;
    box-shadow: 0 -6px 30px rgba(0,0,0,0.04) !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: rgba(0,0,0,0.2) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: var(--text) !important;
    font-size: 0.93rem !important;
    font-family: 'DM Sans', sans-serif !important;
}}
/* Send button inside chat_input */
[data-testid="stChatInput"] button {{
    background: var(--accent) !important;
    color: #fff !important;
    border-radius: 50% !important;
    width: 36px !important; height: 36px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}}
[data-testid="stChatInput"] button:hover {{
    transform: scale(1.15) rotate(15deg) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25) !important;
}}

/* ── Loader ──────────────────────────────── */
.loader {{
    display: flex; align-items: center; gap: 16px;
    padding: 20px 24px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.03);
    animation: slideUp 0.3s ease-out;
}}
.loader-bar {{
    flex: 1;
    height: 4px;
    background: rgba(0,0,0,0.06);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}}
.loader-bar::after {{
    content: "";
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    border-radius: 4px;
    animation: shimmer 1.5s ease-in-out infinite;
}}
@keyframes shimmer {{
    0%   {{ left: -40%; }}
    100% {{ left: 100%; }}
}}
.loader-label {{
    color: var(--text-soft); font-size: 0.82rem;
    font-weight: 500; white-space: nowrap;
}}
.loader-steps {{
    font-size: 0.72rem; color: var(--text-muted);
}}

/* ── Expander ────────────────────────────── */
.streamlit-expanderHeader {{
    font-size: 0.82rem !important;
    color: var(--text-soft) !important;
    font-weight: 600 !important;
}}
details {{
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}}
</style>
""", unsafe_allow_html=True)


# ─── Answer logic ─────────────────────────────────────────────
def answer_question(question: str):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
        return "⚠️ Set GEMINI_API_KEY in .env", []

    docs = fetch_news(topic=question[:50], hours=48)
    if not docs:
        docs = fetch_news(topic="latest news", hours=24)
    if not docs:
        return "⚠️ No news articles found.", []

    pieces, sources = [], []
    for d in docs[:8]:
        pieces.append(d.page_content[:1200])
        sources.append({"title": d.metadata.get("title",""),
                        "source": d.metadata.get("source",""),
                        "url": d.metadata.get("url","#")})

    context = "\n\n---\n\n".join(pieces)[:12000]
    user_prompt = f"NEWS ARTICLES:\n{context}\n\nQUESTION: {question}"
    answer = call_gemini(SYS_PROMPT, user_prompt)
    return answer, sources


# ─── Session state ────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = []
    st.session_state.active = None

def new_chat():
    c = {"id": len(st.session_state.chats)+1, "title": "New Chat", "msgs": []}
    st.session_state.chats.insert(0, c)
    st.session_state.active = c["id"]
    return c

def get_chat():
    if st.session_state.active is None: return None
    for c in st.session_state.chats:
        if c["id"] == st.session_state.active: return c
    return None


# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-head">
        <h2>News Intelligence</h2>
        <p>Powered by Gemini</p>
    </div>""", unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True):
        new_chat(); st.rerun()

    st.markdown('<div class="sb-label">Recent</div>', unsafe_allow_html=True)

    if not st.session_state.chats:
        st.caption("No conversations yet.")
    else:
        for c in st.session_state.chats:
            active = c["id"] == st.session_state.active
            icon = "▸" if active else " "
            if st.button(f"{icon} {c['title']}", key=f"h{c['id']}", use_container_width=True):
                st.session_state.active = c["id"]; st.rerun()


# ─── Main ─────────────────────────────────────────────────────
chat = get_chat()
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

if not chat or not chat["msgs"]:
    st.markdown("""
    <div class="greeting">
        <div class="g-icon">📰</div>
        <h1>Hello, how can I help?</h1>
        <p>Your AI-powered news briefing assistant</p>
        <p class="hint">Try: "What's happening in AI today?" or "Latest cricket news"</p>
    </div>""", unsafe_allow_html=True)
else:
    for m in chat["msgs"]:
        if m["role"] == "user":
            st.markdown(f'''
            <div class="msg user">
                <div class="bub-u">{m["text"]}</div>
                <div class="av av-u">🧑</div>
            </div>''', unsafe_allow_html=True)
        else:
            # AI answer with card
            st.markdown(f'''
            <div class="msg">
                <div class="av av-a">📰</div>
                <div class="answer-card">
                    <div class="answer-header">
                        <span>📰 NEWS BRIEFING</span>
                    </div>
                    <div class="answer-body">
                        {m["text"]}
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)

            if m.get("sources"):
                with st.expander(f"✦ {len(m['sources'])} Sources", expanded=False):
                    for s in m["sources"]:
                        st.markdown(
                            f'<div class="src-card">'
                            f'<div class="src-dot"></div>'
                            f'<div class="src-name">{s["source"]}</div>'
                            f'<div class="src-link"><a href="{s["url"]}" target="_blank">{s["title"][:60]}</a></div>'
                            f'</div>',
                            unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Input ────────────────────────────────────────────────────
query = st.chat_input("Ask me about the news… 🚀")

if query:
    q = query.strip()
    if not q: st.stop()

    if not chat: chat = new_chat()
    if chat["title"] == "New Chat":
        chat["title"] = q[:28] + ("…" if len(q) > 28 else "")

    chat["msgs"].append({"role": "user", "text": q})

    # Show user msg
    st.markdown(f'''
    <div class="msg user">
        <div class="bub-u">{q}</div>
        <div class="av av-u">🧑</div>
    </div>''', unsafe_allow_html=True)

    # Loader
    loader = st.empty()
    loader.markdown('''
    <div class="loader">
        <div class="av av-a" style="width:34px;height:34px;font-size:0.85rem;">📰</div>
        <div style="flex:1;">
            <div class="loader-label">Analysing news for you…</div>
            <div class="loader-steps">Fetching articles → Reading → Summarising</div>
            <div class="loader-bar"></div>
        </div>
    </div>''', unsafe_allow_html=True)

    try:
        answer, sources = answer_question(q)
    except Exception as e:
        answer = f"Error: {str(e)}"
        sources = []

    loader.empty()
    chat["msgs"].append({"role": "ai", "text": answer, "sources": sources})
    st.rerun()
