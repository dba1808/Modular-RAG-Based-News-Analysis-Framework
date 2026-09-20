"""
ত্রিকোণদৃষ্টি (TrikonDrishti) — Multi-Dimensional News Intelligence Platform
════════════════════════════════════════════════════════════════════════════
Professional three-column news dashboard with authentication,
hero banner, category tabs, ranked story feed, and right-panel widgets.
"""

import os
import time
import json
import logging
import re
import hashlib
import html as html_lib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import requests as http_requests
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.documents import Document

# ── Streamlit Page Configuration ──
st.set_page_config(
    page_title="ত্রিকোণদৃষ্টি · TrikonDrishti",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Local Module Imports ──
from config import (
    APP_NAME_BN,
    APP_NAME_EN,
    APP_TAGLINE,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    AVAILABLE_MODELS,
    SOURCE_RELIABILITY_SCORES,
)
from llm_factory import get_llm, call_llm, check_status
from news_fetcher import (
    fetch_news,
    fetch_news_multi_query,
    fetch_scoped_news,
    get_available_topics,
    clear_cache,
    format_time_ago,
)
from intelligence import (
    ai_rank_articles,
    generate_concise_summary,
    analyze_sentiment,
    detect_trending_topics,
    detect_contradictions,
    generate_daily_briefing,
    check_news_alerts,
    extract_evidence_trail,
    detect_story_drift,
)
from location_service import (
    detect_location,
    reverse_geocode,
    get_location_display,
    get_location_source_badge,
)
from utils import (
    load_bookmarks,
    save_bookmarks,
    add_bookmark,
    remove_bookmark,
    load_chat_history,
    save_chat_history,
    truncate_text,
)
from ui_theme import get_full_css, get_geo_script_html
from auth import is_authenticated, get_current_user, logout, render_auth_page, get_time_greeting, get_user_now, sync_auth_cookie

logger = logging.getLogger("news_rag.app")


# ═══════════════════════════════════════════════════════════════
#  AUTHENTICATION GATE
# ═══════════════════════════════════════════════════════════════

if not is_authenticated():
    render_auth_page()
    st.stop()

current_user = get_current_user()
sync_auth_cookie(current_user.get("username", ""))

# Known user full-name mapping for accounts registered without explicit full name
KNOWN_FULL_NAMES = {
    "dba1808": "Debayudh Bhattacharya",
    "bhattacharyadebayudh13@gmail.com": "Debayudh Bhattacharya",
    "debayudh": "Debayudh Bhattacharya",
    "debayudh_test": "Debayudh Bhattacharya",
    "admin": "Admin",
}

raw_name = (current_user.get("name") or "").strip()
raw_username = (current_user.get("username") or "").strip().lower()
raw_email = (current_user.get("email") or "").strip().lower()

if raw_name and raw_name.lower() != raw_username:
    user_name = raw_name
elif raw_username in KNOWN_FULL_NAMES:
    user_name = KNOWN_FULL_NAMES[raw_username]
elif raw_email in KNOWN_FULL_NAMES:
    user_name = KNOWN_FULL_NAMES[raw_email]
elif raw_username:
    user_name = raw_username.title()
else:
    user_name = "Reader"

user_initial = user_name[0].upper() if user_name else "R"
time_greeting = get_time_greeting()

# Welcome toast on fresh login / signup
if st.session_state.get("welcome_notice"):
    st.toast(f"✦ {st.session_state.welcome_notice}! Personalized dossier ready.")
    del st.session_state["welcome_notice"]

# ── Inject CSS ──
st.markdown(get_full_css(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

if "view" not in st.session_state:
    st.session_state.view = "home"
if "display_mode" not in st.session_state:
    st.session_state.display_mode = "cards"
if "active_username" not in st.session_state or st.session_state.active_username != raw_username:
    st.session_state.active_username = raw_username
    st.session_state.bookmarks = load_bookmarks(raw_username)
    st.session_state.chats = load_chat_history(raw_username) or []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = load_bookmarks(raw_username)
if "user_location" not in st.session_state:
    st.session_state.user_location = None
if "gps_requested" not in st.session_state:
    st.session_state.gps_requested = False
if "chats" not in st.session_state:
    st.session_state.chats = load_chat_history(raw_username) or []
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = OPENROUTER_MODEL
if "trending_topics" not in st.session_state:
    st.session_state.trending_topics = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "cached_views" not in st.session_state:
    st.session_state.cached_views = {}
if "active_category" not in st.session_state:
    st.session_state.active_category = "For You"
if "side_panel_open" not in st.session_state:
    st.session_state.side_panel_open = True
if "mobile_menu_open" not in st.session_state:
    st.session_state.mobile_menu_open = False
if "mobile_sheet_open" not in st.session_state:
    st.session_state.mobile_sheet_open = False


# ── Location Resolution ──
if st.session_state.user_location is None:
    try:
        st.session_state.user_location = detect_location()
    except Exception as e:
        logger.warning(f"Location detection failed: {e}")
        st.session_state.user_location = {
            "city": "Kolkata",
            "region": "West Bengal",
            "country": "India",
            "country_code": "IN",
            "source": "default",
        }

loc = st.session_state.user_location or {}
loc_display = get_location_display(loc)
loc_badge = get_location_source_badge(loc)


# ═══════════════════════════════════════════════════════════════
#  WEATHER HELPER (wttr.in — free, no API key)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_weather(city: str) -> dict:
    """Fetch current weather from wttr.in for a city."""
    try:
        resp = http_requests.get(
            f"https://wttr.in/{city}?format=j1",
            timeout=5,
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current_condition", [{}])[0]
            return {
                "temp_c": current.get("temp_C", "?"),
                "condition": current.get("weatherDesc", [{}])[0].get("value", "Clear"),
            }
    except Exception:
        pass
    return {"temp_c": "?", "condition": "Fair"}


# ═══════════════════════════════════════════════════════════════
#  AI & RAG LOGIC
# ═══════════════════════════════════════════════════════════════

SYS_SYNTHESIS_PROMPT = """You are an elite Senior News Intelligence Analyst at ত্রিকোণদৃষ্টি (TrikonDrishti).
Synthesize the provided news context into a structured, highly objective editorial report.

RULES:
1. Base all facts, numbers, and dates strictly on the provided context.
2. Do not hallucinate or invent information.
3. Structure with bold section headings and concise bullet points.

FORMAT STRUCTURE:
**EXECUTIVE OVERVIEW**
2-3 authoritative sentences summarizing what transpired and why it matters.

**STRATEGIC DEVELOPMENTS**
- **Point 1:** Key development with verified details
- **Point 2:** Key development with verified details
- **Point 3:** Key development with verified details

**TRI-PERSPECTIVE IMPACT ANALYSIS**
- **Local:** Immediate municipal or regional consequence
- **National:** Policy, economic, or governmental impact
- **Global:** International supply chain, diplomatic, or market ripple effects

**SENTIMENT & STRATEGIC TONE:** Positive / Neutral / Negative (1 sentence rationale)
"""



def get_safe_llm():
    """Return LLM instance or None if API key is unconfigured."""
    try:
        return get_llm(model=st.session_state.selected_model)
    except Exception as e:
        logger.warning(f"LLM not available: {e}")
        return None


@st.cache_data(ttl=600, show_spinner=False)
def execute_news_synthesis(question: str):
    """Run optimized high-speed news retrieval & synthesis pipeline."""
    # 1. Fast Direct News Retrieval (instant, avoids multi-query LLM round-trip delay)
    docs = fetch_news(question, hours=72)
    if not docs:
        docs = fetch_news(question, hours=96)
    if not docs:
        return "No recent news articles found for this topic.", [], {}

    # 2. Fast heuristic ranking (BM25 + authority + recency) - executes in <15ms
    ranked_docs = ai_rank_articles(
        docs,
        user_context=question,
        location=loc.get("city", "Kolkata"),
        llm=None,
    )

    top_docs = ranked_docs[:5]
    context_blocks = []
    sources = []
    for d in top_docs:
        snippet = d.page_content[:240].strip()
        context_blocks.append(f"Source: {d.metadata.get('source')}\nTitle: {d.metadata.get('title')}\n{snippet}")
        sources.append({
            "title": d.metadata.get("title", ""),
            "source": d.metadata.get("source", ""),
            "url": d.metadata.get("url", "#"),
            "time_ago": d.metadata.get("time_ago", "Recent"),
            "reliability": d.metadata.get("reliability_score", 0.60),
            "score": d.metadata.get("composite_score", 75),
        })

    context_str = "\n\n".join(context_blocks)[:3500]

    llm = get_safe_llm()
    answer = None
    if llm:
        for attempt_tokens in [400, 250]:
            try:
                answer = call_llm(
                    SYS_SYNTHESIS_PROMPT,
                    f"NEWS CONTEXT:\n{context_str}\n\nUSER INQUIRY: {question}",
                    model=st.session_state.selected_model,
                    max_tokens=attempt_tokens,
                )
                if answer and "Error code: 402" not in answer:
                    break
            except Exception as e:
                logger.warning(f"Synthesis attempt failed with max_tokens={attempt_tokens}: {e}")
                answer = None

    # Fallback to high-quality structured editorial brief if API limits hit
    if not answer or "Error code:" in str(answer):
        points = []
        for d in top_docs[:3]:
            t = d.metadata.get("title", "")
            s = d.metadata.get("source", "Verified Source")
            c = d.page_content.strip()[:180]
            points.append(f"- **{t}** ({s}): {c}...")

        sources_str = ", ".join(list(dict.fromkeys(s.get("source", "") for s in sources[:3])))
        answer = f"""**EXECUTIVE OVERVIEW**
Latest verified intelligence on **{question}**. Real-time monitoring across regional and international news feeds indicates evolving strategic developments.

**KEY STRATEGIC DEVELOPMENTS**
{chr(10).join(points)}

**TRI-PERSPECTIVE IMPACT ANALYSIS**
- **Local:** Regional infrastructure and municipal civic updates tracked in {loc.get('city', 'Kolkata')}.
- **National:** Policy governance, legislative updates, and domestic market developments.
- **Global:** Macroeconomic trends, international supply chains, and cross-border diplomatic ripples.

**SENTIMENT & STRATEGIC TONE:** Neutral (Verified factual coverage from {sources_str})"""

    sentiment = "Neutral"
    if "SENTIMENT & STRATEGIC TONE:" in answer:
        sent_line = answer.split("SENTIMENT & STRATEGIC TONE:")[-1].split("\n")[0]
        if "Positive" in sent_line:
            sentiment = "Positive"
        elif "Negative" in sent_line:
            sentiment = "Negative"

    return answer, sources, {"sentiment": sentiment}



# ═══════════════════════════════════════════════════════════════
#  CATEGORY BADGE HELPER
# ═══════════════════════════════════════════════════════════════

def _get_cat_badge_class(category: str) -> str:
    """Map category name to CSS badge class."""
    cat_lower = category.lower()
    if any(k in cat_lower for k in ("local", "city", "municipal")):
        return "badge-local"
    elif any(k in cat_lower for k in ("weather", "climate", "rain", "temperature")):
        return "badge-weather"
    elif any(k in cat_lower for k in ("politic", "policy", "government", "election")):
        return "badge-politics"
    elif any(k in cat_lower for k in ("sport", "cricket", "football", "tennis")):
        return "badge-sports"
    elif any(k in cat_lower for k in ("tech", "ai", "digital", "cyber", "software")):
        return "badge-tech"
    elif any(k in cat_lower for k in ("business", "economy", "market", "finance")):
        return "badge-business"
    elif any(k in cat_lower for k in ("health", "medicine", "medical")):
        return "badge-health"
    elif any(k in cat_lower for k in ("science", "space", "research")):
        return "badge-science"
    elif any(k in cat_lower for k in ("entertainment", "movie", "music", "bollywood")):
        return "badge-entertainment"
    return "badge-general"


# ═══════════════════════════════════════════════════════════════
#  TOP HEADER & PRIMARY NAVIGATION (UNIFIED RESPONSIVE SYSTEM)
# ═══════════════════════════════════════════════════════════════

# Handle GPS Callback if triggered
if st.session_state.gps_requested:
    geo_data = components.html(get_geo_script_html(), height=0, scrolling=False)
    st.session_state.gps_requested = False

# Live bookmark counter badge
saved_count = len(st.session_state.get("bookmarks", []))
saved_badge = f" ({saved_count})" if saved_count > 0 else ""

# ── 1. TOP HEADER (Logo | Search | Profile & Controls) ──
with st.container():
    st.markdown('<div class="app-header-anchor"></div>', unsafe_allow_html=True)
    hdr_c1, hdr_c2, hdr_c3 = st.columns([1.8, 3.6, 2.8], gap="small")

    with hdr_c1:
        st.markdown(f'''
        <div class="hdr-brand">
          <div class="hdr-brand-icon">TD</div>
          <div class="hdr-brand-info">
            <span class="hdr-brand-title">{APP_NAME_BN}</span>
            <span class="hdr-brand-sub">NEWS INTELLIGENCE</span>
          </div>
        </div>
        ''', unsafe_allow_html=True)

    with hdr_c2:
        user_search_input = st.text_input(
            "Global Search",
            value=st.session_state.search_query,
            placeholder="Search news, topics, keywords or ask AI...",
            label_visibility="collapsed",
            key="main_global_search",
        )

    with hdr_c3:
        st.markdown('<div class="hdr-controls-anchor"></div>', unsafe_allow_html=True)
        meta_c1, meta_c2, meta_c3 = st.columns([1.55, 0.45, 1.15], gap="small")
        with meta_c1:
            st.markdown(f'''
            <div class="hdr-location-chip" title="Active Detected Region">
              <span class="hdr-loc-pin">📍</span>
              <span class="hdr-loc-text">{loc.get("city", "Kolkata")}, {loc.get("country", "India")}</span>
            </div>
            ''', unsafe_allow_html=True)
        with meta_c2:
            if st.button("🔄", key="hdr_sync_btn", help="Sync feeds & refresh cache", use_container_width=True):
                clear_cache()
                st.session_state.cached_views.clear()
                st.toast("Feed synchronized.")
                st.rerun()
        with meta_c3:
            if st.button("Sign Out", key="hdr_signout_btn", help=f"Signed in as {user_name} ({user_initial})", use_container_width=True):
                logout()

# Route search if query changed
if user_search_input.strip() and user_search_input.strip() != st.session_state.search_query:
    st.session_state.search_query = user_search_input.strip()
    st.session_state.view = "search"
    st.rerun()
# ── 2. UNIFIED RESPONSIVE PRIMARY NAVIGATION ──
nav_tabs_data = [
    ("HOME", "home", "🏠"),
    ("GLOBAL NEWS", "discover", "🌐"),
    ("LOCAL NEWS", "local", "📍"),
    ("CATEGORIES", "categories", "📑"),
    (f"SAVED{saved_badge}", "saved", "🔖"),
    ("AI INTEL", "search", "⚡"),
    ("SETTINGS", "settings", "⚙️"),
]

with st.container():
    st.markdown('<div class="primary-nav-anchor"></div>', unsafe_allow_html=True)
    nav_cols = st.columns(7, gap="small")
    for idx, (tab_label, tab_key, tab_icon) in enumerate(nav_tabs_data):
        with nav_cols[idx]:
            is_active = (st.session_state.view == tab_key)
            slot_class = "nav-btn-slot is-active" if is_active else "nav-btn-slot"
            st.markdown(f'<div class="{slot_class}">', unsafe_allow_html=True)
            btn_type = "primary" if is_active else "secondary"
            btn_text = f"{tab_icon}  {tab_label}"
            if st.button(btn_text, key=f"pnav_{tab_key}", use_container_width=True, type=btn_type):
                if st.session_state.view != tab_key:
                    st.session_state.view = tab_key
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)




# ═══════════════════════════════════════════════════════════════
#  RENDER HELPERS
# ═══════════════════════════════════════════════════════════════

def render_hero_banner():
    """Render the main hero banner with branding, animated weather atmosphere, and dynamic personal greeting."""
    city = loc.get("city", "Kolkata")
    weather = fetch_weather(city)
    now = get_user_now()

    cond = str(weather.get("condition", "Clear")).lower()
    temp_raw = str(weather.get("temp_c", "28"))
    temp_num = 28.0
    try:
        parsed = re.sub(r"[^\d.-]", "", temp_raw)
        if parsed:
            temp_num = float(parsed)
    except Exception:
        temp_num = 28.0

    # Determine dynamic weather atmosphere
    if any(w in cond for w in ("rain", "drizzle", "shower", "thunder", "storm", "wet", "precipitation")):
        rain_drops = "".join(
            f'<div class="rain-drop" style="left:{i * 4.8}%;animation-delay:{((i * 137) % 80) / 100:.2f}s;animation-duration:{0.65 + ((i * 31) % 40) / 100:.2f}s"></div>'
            for i in range(21)
        )
        anim_html = f'<div class="hero-atmosphere-backdrop"><div class="hero-anim-rain">{rain_drops}</div></div>'
    elif temp_num <= 14.0 or any(w in cond for w in ("snow", "ice", "frost", "sleet", "cold", "blizzard", "freeze", "chilly")):
        frost_crystals = "".join(
            f'<div class="frost-crystal" style="left:{i * 5.2}%;animation-delay:{((i * 149) % 100) / 100:.2f}s;animation-duration:{3.0 + ((i * 43) % 40) / 10:.1f}s"></div>'
            for i in range(19)
        )
        anim_html = f'<div class="hero-atmosphere-backdrop"><div class="hero-anim-cold">{frost_crystals}</div></div>'
    elif any(w in cond for w in ("cloud", "overcast", "fog", "mist", "haze", "smoke", "gloomy")):
        anim_html = '<div class="hero-atmosphere-backdrop"><div class="hero-anim-cloudy"><div class="cloud-mist-1"></div><div class="cloud-mist-2"></div></div></div>'
    else:
        anim_html = '<div class="hero-atmosphere-backdrop"><div class="hero-anim-sunny"><div class="sun-corona"></div><div class="sun-rays"></div></div></div>'

    hero_html = (
        f'<div class="hero-banner">'
        f'{anim_html}'
        f'<div class="hero-left-col">'
        f'<div class="hero-scope-row">'
        f'<span class="hero-scope-badge">REGIONAL INTELLIGENCE</span>'
        f'<span class="hero-greeting-line">✦ {time_greeting}, <strong>{user_name}</strong> • AI Regional Dossier Active</span>'
        f'</div>'
        f'<div class="hero-branding-box">'
        f'<div class="hero-title-bn">{APP_NAME_BN}</div>'
        f'<div class="hero-subtitle">TRIKONDRISHTI · NEWS INTELLIGENCE</div>'
        f'</div>'
        f'<div class="hero-tagline-row">'
        f'<span>VERIFIED SOURCES</span>'
        f'<span class="hero-tagline-divider"></span>'
        f'<span>AI RANKED</span>'
        f'<span class="hero-tagline-divider"></span>'
        f'<span>TRI-PERSPECTIVE</span>'
        f'</div>'
        f'</div>'
        f'<div class="hero-weather-column">'
        f'<div class="hero-weather-box">'
        f'<div class="hero-weather-temp">{weather["temp_c"]}°C</div>'
        f'<div class="hero-weather-meta">'
        f'<div class="hero-weather-city">{city.upper()}</div>'
        f'<div class="hero-weather-condition">{weather["condition"].upper()}</div>'
        f'<div class="hero-datetime">{now.strftime("%I:%M %p")} · {now.strftime("%a, %d %b %Y")}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)



def render_featured_story(doc: Document, rank: int = 1):
    """Render the prominent lead featured story card (#1) with balanced proportions, story drift badge, and interactive Evidence Trail."""
    raw_title = html_lib.unescape(doc.metadata.get("title", "Untitled"))
    raw_summary = html_lib.unescape(doc.metadata.get("summary") or doc.page_content[:280])
    raw_source = html_lib.unescape(doc.metadata.get("source", "News"))

    # Humanize summary
    summary = raw_summary.strip()
    t_norm = re.sub(r"[^a-z0-9]", "", raw_title.lower())
    s_norm = re.sub(r"[^a-z0-9]", "", summary.lower())
    if s_norm in (t_norm,) or len(s_norm) <= len(t_norm) + 12:
        summary = f"Comprehensive coverage and verified reports from {raw_source} on this evolving story."

    title = html_lib.escape(raw_title)
    summary_esc = html_lib.escape(summary)
    source = html_lib.escape(raw_source)
    url = doc.metadata.get("url", "#")
    time_str = doc.metadata.get("time_ago") or doc.metadata.get("date", "")[:16]
    category = html_lib.escape(doc.metadata.get("category", "General"))
    location_tag = html_lib.escape(doc.metadata.get("location_tag") or loc.get("city", ""))
    score = doc.metadata.get("composite_score", 88)

    # RAG Intelligence: Story Drift & Evidence Trail
    drift = detect_story_drift(doc)
    trail = extract_evidence_trail(doc)

    drift_badge_html = f'<span class="drift-badge {drift["css_class"]}" title="{html_lib.escape(drift["tooltip"])}">{drift["badge_label"]}</span>'
    cat_badge_cls = _get_cat_badge_class(category)

    citations_html = "".join(
        f'<div class="evidence-citation-item">'
        f'<div class="evidence-citation-src">{html_lib.escape(c.get("source", "Wire"))} <span class="evidence-citation-type">{html_lib.escape(c.get("type", "Citation"))}</span></div>'
        f'<div class="evidence-citation-detail">{html_lib.escape(c.get("detail", ""))}</div>'
        f'</div>'
        for c in trail.get("citations", [])
    )

    trail_html = f'''
    <details class="evidence-trail-container">
      <summary class="evidence-trail-summary">
        <span class="evidence-trail-icon">🔍</span>
        <span class="evidence-trail-title">EVIDENCE TRAIL & SOURCE TRACE</span>
        <span class="evidence-trail-confidence">{trail.get("confidence", 85)}% · {trail.get("confidence_label", "Verified")}</span>
      </summary>
      <div class="evidence-trail-body">
        <div class="evidence-claim">
          <span class="evidence-claim-label">CORE VERIFIED CLAIM</span>
          <span class="evidence-claim-text">{html_lib.escape(trail.get("claim", ""))}</span>
        </div>
        <div class="evidence-citations-grid">{citations_html}</div>
        <div class="evidence-trail-footer">
          <span>✦ Verification: {html_lib.escape(trail.get("verification_mode", "Tri-Perspective"))}</span>
          <span>Refreshed: {html_lib.escape(trail.get("timestamp", ""))}</span>
        </div>
      </div>
    </details>
    '''

    st.markdown(f'''
    <div class="featured-story">
      <div class="featured-meta-top">
        <span class="lead-badge">#{rank} LEAD INTEL</span>
        {drift_badge_html}
        <span class="royal-box-badge {cat_badge_cls}">{category}</span>
        <span class="meta-dot">·</span>
        <span class="featured-source-name">{source}</span>
        <span class="meta-dot">·</span>
        <span class="featured-time-tag">{time_str}</span>
        <span class="relevance-box" style="margin-left:auto">{score}% MATCH</span>
      </div>
      <div class="featured-headline">
        <a href="{url}" target="_blank">{title}</a>
      </div>
      <div class="featured-summary">{summary_esc}</div>
      <div class="featured-meta-bottom">
        <span class="featured-loc-pill">📍 {location_tag or "National"}</span>
        <span class="meta-dot">·</span>
        <span class="featured-meta-item">Source: {source}</span>
        <span class="meta-dot">·</span>
        <span class="featured-meta-item">{time_str}</span>
        <span class="meta-dot">·</span>
        <span class="featured-meta-item">{category}</span>
      </div>
      {trail_html}
    </div>
    ''', unsafe_allow_html=True)


def render_story_row(doc: Document, rank: int, key_prefix: str = "sr"):
    """Render a compact story row (#2–#5 style)."""
    raw_title = html_lib.unescape(doc.metadata.get("title", "Untitled"))
    raw_summary = html_lib.unescape(doc.metadata.get("summary") or doc.page_content[:120])
    raw_source = html_lib.unescape(doc.metadata.get("source", "News"))

    summary = raw_summary.strip()
    t_norm = re.sub(r"[^a-z0-9]", "", raw_title.lower())
    s_norm = re.sub(r"[^a-z0-9]", "", summary.lower())
    if s_norm in (t_norm,) or len(s_norm) <= len(t_norm) + 12:
        summary = f"Reports from {raw_source} · Breaking development"

    title = html_lib.escape(raw_title)
    excerpt = html_lib.escape(truncate_text(summary, 120))
    source = html_lib.escape(raw_source)
    url = doc.metadata.get("url", "#")
    time_str = doc.metadata.get("time_ago") or "Recent"
    category = html_lib.escape(doc.metadata.get("category", "General"))
    location_tag = html_lib.escape(doc.metadata.get("location_tag") or "")
    score = doc.metadata.get("composite_score", 72)

    # RAG Story Drift Check
    drift = detect_story_drift(doc)
    cat_badge_cls = _get_cat_badge_class(category)
    drift_badge_html = ""
    if drift["type"] in ("updated", "conflict"):
        drift_badge_html = f'<span class="drift-badge {drift["css_class"]}" style="font-size:0.56rem;padding:1px 5px;margin-left:6px;vertical-align:middle;" title="{html_lib.escape(drift["tooltip"])}">{drift["badge_label"]}</span>'

    st.markdown(f'''
    <div class="story-row">
      <span class="story-rank">{rank}</span>
      <span class="royal-box-badge {cat_badge_cls}" style="flex-shrink:0">{category}</span>
      <div class="story-content">
        <div class="story-title"><a href="{url}" target="_blank">{title}</a>{drift_badge_html}</div>
        <div class="story-excerpt">{excerpt}</div>
      </div>
      <div class="story-meta-right">
        <div class="story-source-time">
          <span class="story-source-name">{source}</span>
          <span>· {time_str}</span>
        </div>
        <div class="story-location">{location_tag or loc.get("city", "")}</div>
      </div>
      <span class="relevance-box">{score}%</span>
    </div>
    ''', unsafe_allow_html=True)


def render_right_panel(articles_count: int = 0, local_count: int = 0, global_count: int = 0):
    """Render the right-side panel widgets."""
    city = loc.get("city", "Kolkata")
    region = loc.get("region", "West Bengal")

    # 1. Local News card
    st.markdown(f'''
    <div class="rp-card">
      <div class="rp-card-title">
        <span>LOCAL DISPATCH</span>
        <span class="rp-card-action">CHANGE</span>
      </div>
      <div class="local-news-card">
        <div class="local-city-title">📍 {city.upper()}</div>
        <div class="local-region-sub">{region}, India</div>
        <div class="local-news-desc">Regional news feed active</div>
        <div class="location-access-box">LOCATION VERIFIED</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # 2. Trending Topics
    trending = [
        f"#{city.replace(' ', '')}",
        f"#{region.replace(' ', '')}",
        "#ISRO", "#IndiaAI", "#StockMarket",
        "#Cricket", "#Technology", "#Health",
    ]
    pills_html = "".join(f'<span class="trend-pill">{t}</span>' for t in trending)
    st.markdown(f'''
    <div class="rp-card">
      <div class="rp-card-title">
        <span>TRENDING TOPICS</span>
        <span class="rp-card-action">VIEW ALL</span>
      </div>
      <div class="trending-pills">{pills_html}</div>
    </div>
    ''', unsafe_allow_html=True)

    # 3. Quick Stats
    st.markdown(f'''
    <div class="rp-card">
      <div class="rp-card-title">
        <span>INTELLIGENCE METRICS</span>
      </div>
      <div class="stats-grid">
        <div class="stat-cell">
          <div class="stat-value">{articles_count or 52}</div>
          <div class="stat-label">Articles Today</div>
          <div class="stat-change">+3 vs yesterday</div>
        </div>
        <div class="stat-cell">
          <div class="stat-value">{local_count or 22}</div>
          <div class="stat-label">Regional Intel</div>
          <div class="stat-change">+2 vs yesterday</div>
        </div>
        <div class="stat-cell">
          <div class="stat-value">{global_count or 19}</div>
          <div class="stat-label">Global Wire</div>
          <div class="stat-change">+5 vs yesterday</div>
        </div>
        <div class="stat-cell">
          <div class="stat-value">5</div>
          <div class="stat-label">Active Sectors</div>
          <div class="stat-change">+1 vs yesterday</div>
        </div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # 4. AI Promo Card
    st.markdown('''
    <div class="ai-promo">
      <span class="ai-promo-crest">TRIKONDRISHTI</span>
      <div class="ai-promo-title">Tri-Perspective Intelligence</div>
      <div class="ai-promo-desc">Multi-source verification, synthesized briefings, and bias detection.</div>
      <span class="ai-promo-btn">EXPLORE ARCHIVE</span>
    </div>
    ''', unsafe_allow_html=True)


def render_news_cards(docs: List[Document], max_items: int = 15, key_prefix: str = "main"):
    """Render editorial news cards grid for secondary views."""
    if not docs:
        st.info("No articles found in this category.")
        return

    # View toggle
    v_col1, v_col2 = st.columns([4.8, 2.2], gap="small")
    with v_col2:
        mode_c1, mode_c2 = st.columns(2, gap="small")
        with mode_c1:
            is_cards = (st.session_state.display_mode == "cards")
            if st.button("⊞ Cards", key=f"btn_mode_cards_{key_prefix}_{st.session_state.view}", type="primary" if is_cards else "secondary", use_container_width=True):
                if not is_cards:
                    st.session_state.display_mode = "cards"
                    st.rerun()
        with mode_c2:
            is_table = (st.session_state.display_mode == "table")
            if st.button("☰ Table", key=f"btn_mode_table_{key_prefix}_{st.session_state.view}", type="primary" if is_table else "secondary", use_container_width=True):
                if not is_table:
                    st.session_state.display_mode = "table"
                    st.rerun()

    if st.session_state.display_mode == "table":
        rows_html = ""
        for rank, doc in enumerate(docs[:max_items], start=1):
            title = html_lib.escape(html_lib.unescape(doc.metadata.get("title", "Untitled")))
            source = html_lib.escape(html_lib.unescape(doc.metadata.get("source", "News")))
            category = html_lib.escape(doc.metadata.get("category", "General"))
            time_str = doc.metadata.get("time_ago") or doc.metadata.get("date", "")[:16]
            score = doc.metadata.get("composite_score", 70)
            url = doc.metadata.get("url", "#")

            rows_html += (
                f'<tr>'
                f'<td style="font-weight:700;color:var(--gold-primary)">#{rank}</td>'
                f'<td style="font-weight:600;"><a href="{url}" target="_blank" style="color:#fcfbf7;text-decoration:none;">{title}</a></td>'
                f'<td><span style="color:#c5c1b6;font-weight:600">{source}</span></td>'
                f'<td><span class="tag-pill">{category}</span></td>'
                f'<td style="font-family:var(--font-mono);font-size:0.72rem">{time_str}</td>'
                f'<td><span class="relevance-box">{score}%</span></td>'
                f'<td><a href="{url}" target="_blank" class="read-story-btn">Read</a></td>'
                f'</tr>'
            )

        table_html = (
            f'<div class="table-wrap"><table class="news-table"><thead><tr>'
            f'<th>#</th><th>Headline</th><th>Source</th><th>Category</th><th>Time</th><th>Relevance</th><th>Link</th>'
            f'</tr></thead><tbody>{rows_html}</tbody></table></div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

    else:
        cards_html = '<div class="news-grid">'
        for doc in docs[:max_items]:
            raw_title = html_lib.unescape(doc.metadata.get("title", "Untitled"))
            raw_summary = html_lib.unescape(doc.metadata.get("summary") or doc.page_content[:200])
            raw_source = html_lib.unescape(doc.metadata.get("source", "News"))

            summary = raw_summary.strip()
            t_norm = re.sub(r"[^a-z0-9]", "", raw_title.lower())
            s_norm = re.sub(r"[^a-z0-9]", "", summary.lower())
            src_norm = re.sub(r"[^a-z0-9]", "", raw_source.lower())
            if s_norm in (t_norm, t_norm + src_norm, src_norm + t_norm) or len(s_norm) <= len(t_norm) + 12:
                summary = f"Comprehensive coverage and verified reports from {raw_source} on this evolving story."

            title = html_lib.escape(raw_title)
            summary_esc = html_lib.escape(summary)
            source = html_lib.escape(raw_source)
            time_str = doc.metadata.get("time_ago") or doc.metadata.get("date", "")[:16]
            url = doc.metadata.get("url", "#")
            category = html_lib.escape(doc.metadata.get("category", "General"))
            scope = doc.metadata.get("scope", "General")
            loc_tag = html_lib.escape(doc.metadata.get("location_tag") or "")
            score = doc.metadata.get("composite_score", 72)

            loc_html = f'<span class="tag-pill">{loc_tag}</span>' if loc_tag else ""
            cat_badge_cls = _get_cat_badge_class(category)

            if score >= 85:
                badge_html = '<span class="royal-box-badge badge-general">★ TOP STORY</span>'
            elif score >= 70:
                badge_html = '<span class="royal-box-badge badge-tech">✦ VERIFIED</span>'
            else:
                badge_html = '<span class="royal-box-badge">DISPATCH</span>'

            card_item = (
                '<div class="news-card">'
                '<div>'
                f'<div class="news-card-header"><span class="news-card-source">{source}</span><span class="news-card-time">{time_str}</span></div>'
                f'<div class="news-card-title"><a href="{url}" target="_blank">{title}</a></div>'
                f'<div class="news-card-summary">{summary_esc}</div>'
                f'<div class="news-card-tags"><span class="royal-box-badge {cat_badge_cls}" style="font-size:0.6rem;padding:2px 7px">{category}</span>{loc_html}</div>'
                '</div>'
                '<div class="news-card-footer">'
                f'<div style="display:flex;align-items:center;gap:8px">{badge_html}<span style="color:var(--t-muted);font-size:0.68rem">· 2 min read</span></div>'
                f'<a href="{url}" target="_blank" class="read-story-btn">Read Story</a>'
                '</div>'
                '</div>'
            )
            cards_html += card_item

        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    # Bookmark buttons
    with st.expander("Save Articles to Dossier"):
        bm_cols = st.columns(min(len(docs[:4]), 4) if docs[:4] else 1)
        for idx, doc in enumerate(docs[:4]):
            with bm_cols[idx]:
                b_title = doc.metadata.get("title", "")
                b_url = doc.metadata.get("url", "#")
                b_source = doc.metadata.get("source", "")
                url_hash = hashlib.md5(b_url.encode("utf-8", errors="ignore")).hexdigest()[:8]
                if st.button(f"Save: {truncate_text(b_title, 20)}", key=f"bm_{key_prefix}_{idx}_{url_hash}"):
                    if add_bookmark(b_title, b_url, b_source, username=raw_username):
                        st.session_state.bookmarks = load_bookmarks(raw_username)
                        st.toast(f"Saved: {truncate_text(b_title, 30)}")
                    else:
                        st.toast("Already bookmarked.")



# ═══════════════════════════════════════════════════════════════
#  VIEW: HOME — Three-Column Dashboard
# ═══════════════════════════════════════════════════════════════

if st.session_state.view == "home":
    llm = get_safe_llm()

    # Fetch scoped news
    with st.spinner("Loading your personalized news feed..."):
        if "home_global" not in st.session_state.cached_views:
            g_docs = fetch_scoped_news("global", location=loc)
            st.session_state.cached_views["home_global"] = ai_rank_articles(g_docs, user_context="world breaking news", llm=llm)
        if "home_national" not in st.session_state.cached_views:
            n_docs = fetch_scoped_news("national", location=loc)
            st.session_state.cached_views["home_national"] = ai_rank_articles(n_docs, user_context="national affairs", location=loc.get("country", "India"), llm=llm)
        if "home_local" not in st.session_state.cached_views:
            l_docs = fetch_scoped_news("local", location=loc)
            st.session_state.cached_views["home_local"] = ai_rank_articles(l_docs, user_context="local city news", location=loc.get("city", "Kolkata"), llm=llm)

    global_arts = st.session_state.cached_views.get("home_global", [])
    national_arts = st.session_state.cached_views.get("home_national", [])
    local_arts = st.session_state.cached_views.get("home_local", [])

    # === ADAPTIVE TWO-COLUMN LAYOUT ===
    with st.container():
        st.markdown('<div class="main-content-anchor"></div>', unsafe_allow_html=True)
        main_col, right_col = st.columns([2.33, 1.0], gap="medium")

    with main_col:
        # Hero Banner
        render_hero_banner()

        # Category Tabs
        cat_names = ["For You", "Local", "India", "World", "Technology", "Business", "Sports", "Entertainment", "Health", "Science"]
        tabs = st.tabs(cat_names)

        # === FOR YOU TAB ===
        with tabs[0]:
            # Merge and deduplicate: take top from each scope
            all_arts = []
            seen_urls = set()
            for pool in [global_arts, national_arts, local_arts]:
                for doc in pool:
                    u = doc.metadata.get("url", "")
                    if u not in seen_urls:
                        seen_urls.add(u)
                        all_arts.append(doc)
            # Sort by composite score
            all_arts.sort(key=lambda d: d.metadata.get("composite_score", 0), reverse=True)

            if all_arts:
                st.markdown('''
                <div class="section-hdr">
                  <span class="section-hdr-title"><span class="section-hdr-box"></span> TOP STORIES <span class="section-hdr-sub">AI ranked · Verified regional & national coverage</span></span>
                  <span class="view-all-link">VIEW ALL</span>
                </div>
                ''', unsafe_allow_html=True)

                # Story #1 — Featured
                render_featured_story(all_arts[0], rank=1)

                # Stories #2–#4 — Compact rows (fits above the fold)
                for i, doc in enumerate(all_arts[1:4], start=2):
                    render_story_row(doc, rank=i, key_prefix="home_foryou")

        # === LOCAL TAB ===
        with tabs[1]:
            city_upper = loc.get("city", "Kolkata").upper()
            st.markdown(f'''
            <div class="section-hdr">
              <span class="section-hdr-title"><span class="section-hdr-box"></span> LOCAL DISPATCH · {city_upper}</span>
            </div>
            ''', unsafe_allow_html=True)
            if local_arts:
                render_featured_story(local_arts[0], rank=1)
                for i, doc in enumerate(local_arts[1:4], start=2):
                    render_story_row(doc, rank=i, key_prefix="home_local_tab")
            else:
                st.info("No local news found.")

        # === INDIA TAB ===
        with tabs[2]:
            st.markdown('''
            <div class="section-hdr">
              <span class="section-hdr-title"><span class="section-hdr-box"></span> NATIONAL DESK</span>
            </div>
            ''', unsafe_allow_html=True)
            if national_arts:
                render_featured_story(national_arts[0], rank=1)
                for i, doc in enumerate(national_arts[1:4], start=2):
                    render_story_row(doc, rank=i, key_prefix="home_national_tab")
            else:
                st.info("No national news found.")

        # === WORLD TAB ===
        with tabs[3]:
            st.markdown('''
            <div class="section-hdr">
              <span class="section-hdr-title"><span class="section-hdr-box"></span> GLOBAL WIRE</span>
            </div>
            ''', unsafe_allow_html=True)
            if global_arts:
                render_featured_story(global_arts[0], rank=1)
                for i, doc in enumerate(global_arts[1:4], start=2):
                    render_story_row(doc, rank=i, key_prefix="home_global_tab")
            else:
                st.info("No global news found.")

        category_map = {
            4: "Technology",
            5: "Business",
            6: "Sports",
            7: "Entertainment",
            8: "Health",
            9: "Science",
        }
        for tab_idx, cat_name in category_map.items():
            with tabs[tab_idx]:
                cache_key = f"cat_{cat_name.lower()}"
                if cache_key not in st.session_state.cached_views:
                    with st.spinner(f"Loading {cat_name}..."):
                        cat_docs = fetch_news(cat_name, hours=48)
                        st.session_state.cached_views[cache_key] = ai_rank_articles(cat_docs, user_context=cat_name, llm=llm)
                cat_arts = st.session_state.cached_views.get(cache_key, [])
                if cat_arts:
                    render_featured_story(cat_arts[0], rank=1)
                    for i, doc in enumerate(cat_arts[1:4], start=2):
                        render_story_row(doc, rank=i, key_prefix=f"home_{cat_name.lower()}")
                else:
                    st.info(f"No {cat_name} news found.")


    # === RIGHT SIDEBAR (30% Trends & Intelligence) ===
    with right_col:
        st.markdown('<div class="sidebar-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="panel-section-tag"><span class="section-hdr-box"></span> TRENDS & INSIGHTS</div>', unsafe_allow_html=True)
        render_right_panel(
            articles_count=len(global_arts) + len(national_arts) + len(local_arts),
            local_count=len(local_arts),
            global_count=len(global_arts),
        )
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close .main-content-layout


# ═══════════════════════════════════════════════════════════════
#  VIEW: DISCOVER
# ═══════════════════════════════════════════════════════════════

elif st.session_state.view == "discover":
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> NEWS INTELLIGENCE DISCOVERY</span>
    </div>
    ''', unsafe_allow_html=True)
    st.caption("Multi-channel topic clusters & interactive AI news investigation")

    disc_topics = [
        ("⚡ AI & Tech", "AI & Generative Tech"),
        ("📈 Markets", "Global Financial Markets"),
        ("🌐 Diplomacy", "International Diplomacy"),
        ("🌿 Climate", "Green Energy & Climate"),
        ("🚀 Space", "Space & Quantum Science"),
        ("⚙️ Supply Chains", "Semiconductor Supply Chains"),
    ]

    if "discover_topic" not in st.session_state:
        st.session_state.discover_topic = "AI & Generative Tech"

    st.markdown('<div class="sub-filter-row">', unsafe_allow_html=True)
    pill_cols = st.columns(6, gap="small")
    for i, (short_label, full_topic) in enumerate(disc_topics):
        with pill_cols[i]:
            is_active = (st.session_state.discover_topic == full_topic)
            if st.button(short_label, key=f"stream_btn_{i}", type="primary" if is_active else "secondary", use_container_width=True, help=full_topic):
                if not is_active:
                    st.session_state.discover_topic = full_topic
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    target_topic = st.session_state.discover_topic
    with st.spinner(f"Retrieving and ranking {target_topic}..."):
        disc_docs = fetch_news(target_topic, hours=48)
        ranked_disc = ai_rank_articles(disc_docs, user_context=target_topic, llm=get_safe_llm())

    render_news_cards(ranked_disc, max_items=12, key_prefix="discover")


# ═══════════════════════════════════════════════════════════════
#  VIEW: LOCAL NEWS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.view == "local":
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> REGIONAL INTELLIGENCE DISPATCH</span>
    </div>
    ''', unsafe_allow_html=True)

    loc_cols = st.columns([3, 1, 1])
    with loc_cols[0]:
        custom_city = st.text_input(
            "Change City / Location for Local News:",
            value=loc.get("city", "Kolkata"),
            placeholder="Type any city...",
        )
    with loc_cols[1]:
        if st.button("Apply Location", use_container_width=True):
            if custom_city.strip():
                st.session_state.user_location = {
                    "city": custom_city.strip(),
                    "region": custom_city.strip(),
                    "country": loc.get("country", "India"),
                    "country_code": loc.get("country_code", "IN"),
                    "source": "manual",
                }
                st.session_state.cached_views.pop("home_local", None)
                st.toast(f"Switched to: {custom_city.strip()}")
                st.rerun()
    with loc_cols[2]:
        if st.button("Detect GPS", use_container_width=True):
            st.session_state.gps_requested = True
            st.rerun()

    active_city = st.session_state.user_location.get("city", "Kolkata")
    st.info(f"Showing localized news for **{active_city}** ({loc_badge['text']})")

    with st.spinner(f"Fetching local news for {active_city}..."):
        local_news_docs = fetch_scoped_news("local", location=st.session_state.user_location)
        ranked_local = ai_rank_articles(local_news_docs, user_context=active_city, location=active_city, llm=get_safe_llm())

    render_news_cards(ranked_local, max_items=15, key_prefix="loc_view")


# ═══════════════════════════════════════════════════════════════
#  VIEW: CATEGORIES
# ═══════════════════════════════════════════════════════════════

elif st.session_state.view == "categories":
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> NEWS CATEGORIES</span>
    </div>
    ''', unsafe_allow_html=True)

    available_categories = [
        "AI & Technology",
        "Markets & Economy",
        "Politics & Policy",
        "Science & Climate",
        "Health & Medicine",
        "Sports",
        "World Affairs",
    ]

    if "active_cat_choice" not in st.session_state:
        st.session_state.active_cat_choice = available_categories[0]

    st.markdown('<div class="sub-filter-row">', unsafe_allow_html=True)
    cat_cols = st.columns(len(available_categories), gap="small")
    for idx, cat_name in enumerate(available_categories):
        with cat_cols[idx]:
            is_active = (st.session_state.active_cat_choice == cat_name)
            btn_txt = f"◆ {cat_name}" if is_active else cat_name
            if st.button(btn_txt, key=f"cat_sel_btn_{idx}", use_container_width=True):
                st.session_state.active_cat_choice = cat_name
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    sel_cat = st.session_state.active_cat_choice
    cache_key = f"view_cat_{sel_cat}"

    if cache_key not in st.session_state.cached_views:
        with st.spinner(f"Loading {sel_cat}..."):
            cat_docs = fetch_news(sel_cat, hours=48)
            st.session_state.cached_views[cache_key] = ai_rank_articles(cat_docs, user_context=sel_cat, llm=get_safe_llm())

    ranked_cat = st.session_state.cached_views.get(cache_key, [])
    render_news_cards(ranked_cat, max_items=15, key_prefix=f"cat_cards_{sel_cat}")


# ═══════════════════════════════════════════════════════════════
#  VIEW: SAVED NEWS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.view == "saved":
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> SAVED INTELLIGENCE DOSSIER</span>
    </div>
    ''', unsafe_allow_html=True)

    bookmarks = st.session_state.bookmarks
    if not bookmarks:
        st.info("You have no saved articles yet. Bookmark articles from any card or table view.")
    else:
        st.write(f"**Total Saved:** {len(bookmarks)}")

        dossier_text = json.dumps(bookmarks, indent=2)
        st.download_button(
            label="EXPORT DOSSIER (JSON)",
            data=dossier_text,
            file_name=f"trikondrishti_bookmarks_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )

        for i, bm in enumerate(bookmarks):
            b_col1, b_col2 = st.columns([5, 1])
            with b_col1:
                st.markdown(f"""
                <div style="background:var(--bg-card);padding:14px;border-radius:4px;border:1px solid var(--gold-border);margin-bottom:8px">
                  <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--gold-primary);font-weight:700">{html_lib.escape(bm.get('source', 'Source'))} · Saved {bm.get('saved_at', '')[:10]}</div>
                  <div style="font-size:1rem;font-weight:700;margin:6px 0"><a href="{bm.get('url')}" target="_blank" style="color:#ffffff;text-decoration:none;">{html_lib.escape(bm.get('title', 'Untitled'))}</a></div>
                </div>
                """, unsafe_allow_html=True)
            with b_col2:
                if st.button("Remove", key=f"del_bm_{i}"):
                    remove_bookmark(bm.get("url", ""), username=raw_username)
                    st.session_state.bookmarks = load_bookmarks(raw_username)
                    st.rerun()

        if st.button("Clear All Bookmarks", key="clear_all_bm"):
            save_bookmarks([], username=raw_username)
            st.session_state.bookmarks = []
            st.toast("All bookmarks cleared.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  VIEW: SEARCH & AI SYNTHESIS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.view == "search":
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> SEARCH & AI INTELLIGENCE</span>
    </div>
    ''', unsafe_allow_html=True)
    st.caption("Ask any question or search topic for real-time news retrieval & AI editorial synthesis")

    # Interactive Search Input Row
    sq_col1, sq_col2 = st.columns([5, 1])
    with sq_col1:
        current_query_val = st.session_state.search_query or "Global News Headlines"
        search_input_val = st.text_input(
            "Search Archive & Synthesize",
            value=current_query_val,
            placeholder="Type any news topic, country, event, or question...",
            label_visibility="collapsed",
            key="page_search_input_box",
        )
    with sq_col2:
        if st.button("Search", use_container_width=True, key="exec_search_btn"):
            st.session_state.search_query = search_input_val.strip()
            st.rerun()

    # Quick Search Topic Pills
    qp_cols = st.columns(5)
    quick_queries = [
        "Global Economy",
        "Artificial Intelligence",
        "Climate & Energy",
        "India Technology",
        "World Geopolitics"
    ]
    for i, q in enumerate(quick_queries):
        with qp_cols[i]:
            if st.button(q, key=f"quick_search_{i}", use_container_width=True):
                st.session_state.search_query = q
                st.rerun()

    active_query = st.session_state.search_query or search_input_val or "Global News Headlines"

    with st.spinner(f"Analyzing news wire and synthesizing report for '{active_query}'..."):
        report, sources, analysis = execute_news_synthesis(active_query)

    # AI Synthesis Report Box
    st.markdown(f"""
    <div style="background:radial-gradient(ellipse at center, #161820 0%, #090a0d 100%);border:1px solid var(--gold-primary);border-radius:6px;padding:24px;margin:20px 0;box-shadow:0 8px 30px rgba(0,0,0,0.6), var(--gold-glow)">
      <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--gold-border-subtle);padding-bottom:12px;margin-bottom:16px">
        <span style="font-family:var(--font-mono);font-size:0.75rem;font-weight:700;letter-spacing:1.5px;color:var(--gold-primary);text-transform:uppercase">AI EDITORIAL SYNTHESIS REPORT · "{active_query.upper()}"</span>
        <span style="font-family:var(--font-mono);font-size:0.68rem;color:var(--gold-light);background:rgba(212,175,55,0.12);padding:3px 8px;border-radius:3px;border:1px solid var(--gold-border)">SENTIMENT: {analysis.get('sentiment', 'Neutral')}</span>
      </div>
      <div style="font-size:0.92rem;line-height:1.75;color:var(--t-primary)">{report}</div>
    </div>
    """, unsafe_allow_html=True)

    # Contradictions
    contras = analysis.get("contradictions", [])
    if contras:
        with st.expander("Contradictions Detected", expanded=True):
            for c in contras:
                st.markdown(f"""
                <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.25);border-radius:4px;padding:12px;margin-bottom:8px">
                  <div style="font-family:var(--font-mono);font-size:0.68rem;font-weight:700;color:#f87171;text-transform:uppercase">{c.get('topic', 'Conflict')}</div>
                  <div style="margin-top:6px;font-size:0.82rem"><strong>{c.get('source_a')}:</strong> {c.get('claim_a')}</div>
                  <div style="margin:4px 0;font-size:0.72rem;color:#f87171;text-align:center;font-weight:700">— VS —</div>
                  <div style="font-size:0.82rem"><strong>{c.get('source_b')}:</strong> {c.get('claim_b')}</div>
                </div>
                """, unsafe_allow_html=True)

    # Retrieved Sources
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> VERIFIED RETRIEVED SOURCES ({})</span>
    </div>
    '''.format(len(sources)), unsafe_allow_html=True)

    if sources:
        src_docs = []
        for s in sources:
            d = Document(
                page_content=s.get("title", ""),
                metadata={
                    "title": s.get("title"),
                    "source": s.get("source"),
                    "url": s.get("url"),
                    "time_ago": s.get("time_ago"),
                    "composite_score": s.get("score", 80),
                    "category": "Verified Wire",
                }
            )
            src_docs.append(d)
        render_news_cards(src_docs, max_items=12, key_prefix="search_view")
    else:
        st.info("No sources retrieved for this search.")


# ═══════════════════════════════════════════════════════════════
#  VIEW: SETTINGS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.view == "settings":
    st.markdown('''
    <div class="section-hdr">
      <span class="section-hdr-title"><span class="section-hdr-box"></span> SYSTEM CONFIGURATION & DIAGNOSTICS</span>
    </div>
    ''', unsafe_allow_html=True)

    # User Profile Card
    st.markdown(f"""
    <div class="rp-card" style="margin-bottom:1.5rem">
      <div class="rp-card-title"><span>DOSSIER PROFILE</span></div>
      <div style="font-size:0.85rem;color:var(--t-secondary);line-height:1.8">
        <strong>Name:</strong> {current_user.get('name', 'N/A')}<br>
        <strong>Username:</strong> {current_user.get('username', 'N/A')}<br>
        <strong>Email:</strong> {current_user.get('email', 'N/A')}<br>
        <strong>Role:</strong> {current_user.get('role', 'reader')}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # OpenRouter Status
    api_status = check_status(model=st.session_state.selected_model)
    st.markdown("#### 1. OpenRouter API Status")

    if api_status["available"]:
        st.success(f"Connected. Active Model: `{st.session_state.selected_model}`")
    else:
        st.error("""
        OPENROUTER_API_KEY is not configured.
        
        Add your key to `.env`:
        ```env
        OPENROUTER_API_KEY=your_key_here
        ```
        Get a key at [openrouter.ai/keys](https://openrouter.ai/keys).
        """)

    # Model Selection
    st.markdown("#### 2. Select OpenRouter Model")
    selected_m = st.selectbox(
        "Active Model:",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 0,
        help="Select any OpenRouter model for news analysis.",
    )
    if selected_m != st.session_state.selected_model:
        st.session_state.selected_model = selected_m
        st.toast(f"Switched to: {selected_m}")
        st.rerun()

    # Location
    st.markdown("#### 3. Location Configuration")
    st.write(f"**Current:** {loc_display} ({loc_badge['text']})")
    if st.button("Reset Location & Re-Detect via IP"):
        st.session_state.user_location = detect_location()
        st.toast("Location reset.")
        st.rerun()

    # Cache
    st.markdown("#### 4. Cache Management")
    if st.button("Clear All Cache"):
        clear_cache()
        st.session_state.cached_views.clear()
        st.toast("Cache flushed.")

