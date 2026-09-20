"""
UI Theme Module — ত্রিকোণদৃষ্টি (TrikonDrishti) Royal Editorial Design System
═══════════════════════════════════════════════════════════════════════════════
Obsidian Black & Imperial Gold Palette with professional structured boxes,
dynamic weather atmosphere animations (rain, cloud drift, sun solar flare, cold shiver),
compact above-the-fold layout, and zero emojis.
"""


def get_full_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Hind+Siliguri:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  /* Obsidian Black & Imperial Gold Palette */
  --bg-main: #08090b;
  --bg-sidebar: #050607;
  --bg-card: #0e1014;
  --bg-card-hover: #14171e;
  --bg-surface: #121419;
  --bg-input: #0b0c0f;

  /* Gold Trims & Accents */
  --gold-primary: #d4af37;
  --gold-light: #f7e8b6;
  --gold-dim: #9c8030;
  --gold-dark: #634f18;
  --gold-border: rgba(212, 175, 55, 0.24);
  --gold-border-bright: rgba(212, 175, 55, 0.65);
  --gold-border-subtle: rgba(212, 175, 55, 0.12);
  --gold-glow: 0 0 20px rgba(212, 175, 55, 0.14);
  --gold-gradient: linear-gradient(135deg, #d4af37 0%, #f9e9be 50%, #aa7c22 100%);
  --gold-soft-bg: rgba(212, 175, 55, 0.06);

  /* Typography Colors */
  --t-primary: #fcfbf7;
  --t-secondary: #c5c1b6;
  --t-muted: #78736a;
  --t-gold: #e2c05e;

  /* Functional Accents */
  --accent-green: #22c55e;
  --accent-green-subtle: rgba(34, 197, 94, 0.12);
  --accent-red: #ef4444;
  --accent-red-subtle: rgba(239, 68, 68, 0.12);

  /* Fonts */
  --font-serif: 'Cinzel', Georgia, serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-bn: 'Hind Siliguri', 'Cinzel', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Geometry - Crisp luxury corners */
  --radius: 4px;
  --radius-sm: 3px;
  --radius-lg: 6px;
}

/* ── Global Base ── */
html, body, [class*="css"], .stApp {
  font-family: var(--font-sans) !important;
  color: var(--t-primary) !important;
  background-color: var(--bg-main) !important;
  -webkit-font-smoothing: antialiased;
}

#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] {
  background: transparent !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: visible !important;
}
.stDeployButton { display: none !important; }

/* Compact Viewport - Prevents going down too much */
.block-container {
  padding-top: 0.4rem !important;
  padding-bottom: 1.2rem !important;
  padding-left: 1.4rem !important;
  padding-right: 1.4rem !important;
  max-width: 100% !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: var(--bg-main);
}
::-webkit-scrollbar-thumb {
  background: var(--gold-border);
  border-radius: 2px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--gold-primary);
}

/* ═══════════════════════════════════════
   SIDEBAR — 3D Book Animation & Royal Gold Spine
   ═══════════════════════════════════════ */
@keyframes sidebarBookUnfold {
  0% {
    transform: perspective(1400px) rotateY(-75deg);
    transform-origin: left center;
    opacity: 0.15;
    box-shadow: 0 0 0 rgba(0,0,0,0);
  }
  60% {
    transform: perspective(1400px) rotateY(-10deg);
    opacity: 0.95;
    box-shadow: 20px 0 40px rgba(0,0,0,0.9), 0 0 25px rgba(212, 175, 55, 0.3);
  }
  100% {
    transform: perspective(1400px) rotateY(0deg);
    transform-origin: left center;
    opacity: 1;
    box-shadow: 15px 0 35px rgba(0,0,0,0.85), 0 0 20px rgba(212, 175, 55, 0.25);
  }
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #07090d 0%, #0a0d12 100%) !important;
  border-right: 3px solid var(--gold-primary) !important;
  box-shadow: 15px 0 35px rgba(0,0,0,0.85), 0 0 20px rgba(212, 175, 55, 0.25) !important;
  width: 255px !important;
  min-width: 255px !important;
  animation: sidebarBookUnfold 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
}

section[data-testid="stSidebar"] .block-container {
  padding: 0.75rem 0.7rem !important;
}

/* Streamlit Sidebar Collapse (Small Cross ✕) Button */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarHeader"] {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-end !important;
}

[data-testid="stSidebarCollapseButton"] button,
button[data-testid="stSidebarCollapseButton"] {
  background: rgba(212, 175, 55, 0.15) !important;
  border: 1px solid var(--gold-primary) !important;
  border-radius: 50% !important;
  color: var(--gold-light) !important;
  width: 30px !important;
  height: 30px !important;
  min-width: 30px !important;
  max-width: 30px !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.2) !important;
  cursor: pointer !important;
}

[data-testid="stSidebarCollapseButton"] button *,
button[data-testid="stSidebarCollapseButton"] * {
  display: none !important;
}

[data-testid="stSidebarCollapseButton"] button::after,
button[data-testid="stSidebarCollapseButton"]::after {
  content: '✕' !important;
  font-family: var(--font-sans) !important;
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: var(--gold-light) !important;
  line-height: 1 !important;
  display: block !important;
}

[data-testid="stSidebarCollapseButton"] button:hover,
button[data-testid="stSidebarCollapseButton"]:hover {
  background: var(--gold-primary) !important;
  color: #000000 !important;
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.6) !important;
  transform: rotate(90deg) scale(1.12) !important;
}

[data-testid="stSidebarCollapseButton"] button:hover::after,
button[data-testid="stSidebarCollapseButton"]:hover::after {
  color: #000000 !important;
}

/* Streamlit Sidebar Expand — Clean Gold Royal Menu Button */
@keyframes menuPulse {
  0% { box-shadow: 0 4px 18px rgba(0,0,0,0.85), 0 0 10px rgba(212, 175, 55, 0.35); }
  50% { box-shadow: 0 4px 22px rgba(0,0,0,0.95), 0 0 20px rgba(212, 175, 55, 0.65); transform: scale(1.03); }
  100% { box-shadow: 0 4px 18px rgba(0,0,0,0.85), 0 0 10px rgba(212, 175, 55, 0.35); }
}

[data-testid="stExpandSidebarButton"],
button[data-testid="stExpandSidebarButton"],
div[data-testid="collapsedControl"] button {
  display: flex !important;
  visibility: visible !important;
  position: fixed !important;
  top: 10px !important;
  left: 10px !important;
  z-index: 999999 !important;
  background: radial-gradient(circle, #241c0e 0%, #0d0f14 100%) !important;
  border: 1.8px solid var(--gold-primary) !important;
  border-radius: var(--radius) !important;
  color: var(--gold-light) !important;
  width: 38px !important;
  height: 38px !important;
  min-width: 38px !important;
  max-width: 38px !important;
  padding: 0 !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
  cursor: pointer !important;
  animation: menuPulse 4s infinite ease-in-out !important;
}

[data-testid="stExpandSidebarButton"] *,
button[data-testid="stExpandSidebarButton"] *,
div[data-testid="collapsedControl"] button * {
  display: none !important;
}

[data-testid="stExpandSidebarButton"]::after,
button[data-testid="stExpandSidebarButton"]::after,
div[data-testid="collapsedControl"] button::after {
  content: '☰' !important;
  font-size: 1.25rem !important;
  font-weight: 700 !important;
  color: var(--gold-light) !important;
  line-height: 1 !important;
  display: inline-block !important;
  filter: drop-shadow(0 0 4px rgba(212,175,55,0.6));
}

[data-testid="stExpandSidebarButton"]:hover,
button[data-testid="stExpandSidebarButton"]:hover,
div[data-testid="collapsedControl"] button:hover {
  transform: scale(1.08) !important;
  border-color: var(--gold-light) !important;
  box-shadow: 0 6px 25px rgba(0,0,0,0.95), 0 0 25px rgba(212, 175, 55, 0.75) !important;
  background: radial-gradient(circle, #352814 0%, #161922 100%) !important;
}

/* Sidebar Top Bar Indicator */
.sb-book-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--gold-border-subtle);
}

.sb-book-header-label {
  font-family: var(--font-serif);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

/* Sidebar Brand */
.sb-brand {
  padding: 0.1rem 0.2rem 0.7rem;
  border-bottom: 1px solid var(--gold-border);
  margin-bottom: 0.65rem;
  text-align: left;
}

.sb-brand-icon {
  width: 38px;
  height: 38px;
  border: 1px solid var(--gold-primary);
  background: linear-gradient(135deg, #18150c 0%, #0a0c10 100%);
  border-radius: 3px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-size: 0.92rem;
  font-weight: 800;
  color: var(--gold-primary);
  letter-spacing: 1px;
  margin-bottom: 8px;
  box-shadow: var(--gold-glow);
}

.sb-brand-bn {
  font-family: var(--font-bn) !important;
  font-size: 1.35rem;
  font-weight: 700;
  color: #ffffff;
  display: block;
  letter-spacing: 0.5px;
  line-height: 1.15;
}

.sb-savage-tagline {
  font-family: var(--font-mono);
  font-size: 0.61rem;
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 1.1px;
  text-transform: uppercase;
  margin-top: 8px;
  padding: 5px 8px;
  background: rgba(212, 175, 55, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-left: 3px solid var(--gold-primary);
  border-radius: 2px;
  line-height: 1.4;
  display: block;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}

/* Sidebar Boxed Sections */
.sb-box {
  background: linear-gradient(180deg, #141720 0%, #0d0f14 100%);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius);
  padding: 0.65rem 0.75rem 0.5rem;
  margin-bottom: 0.75rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  transition: all 0.2s ease;
}

.sb-box:hover {
  border-color: rgba(212, 175, 55, 0.5);
  box-shadow: 0 6px 20px rgba(0,0,0,0.6), 0 0 12px rgba(212, 175, 55, 0.14);
}

.sb-box-title {
  font-family: var(--font-serif);
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--gold-primary);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 0.4rem;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--gold-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sb-badge-pill {
  font-family: var(--font-mono);
  font-size: 0.52rem;
  padding: 1px 5px;
  border-radius: 2px;
  background: rgba(212, 175, 55, 0.12);
  color: var(--gold-light);
  border: 1px solid var(--gold-border);
  letter-spacing: 0.5px;
}

.sb-user-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 6px;
  padding: 5px 8px;
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  border: 1px solid var(--gold-border-subtle);
}

.sb-user-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.3px;
}

.sb-user-role {
  font-family: var(--font-mono);
  font-size: 0.55rem;
  color: #4ade80;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* Sidebar Navigation Buttons */
section[data-testid="stSidebar"] .stButton > button {
  width: 100% !important;
  text-align: left !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  background: var(--bg-surface) !important;
  border: 1px solid var(--gold-border-subtle) !important;
  border-left: 2px solid transparent !important;
  color: var(--t-secondary) !important;
  font-size: 0.69rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase !important;
  padding: 0.35rem 0.6rem !important;
  border-radius: var(--radius-sm) !important;
  margin-bottom: 2px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
  background: linear-gradient(90deg, rgba(212, 175, 55, 0.18) 0%, rgba(212, 175, 55, 0.05) 100%) !important;
  border-color: var(--gold-primary) !important;
  border-left: 2px solid var(--gold-primary) !important;
  color: #ffffff !important;
  transform: translateX(3px) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.5), 0 0 10px rgba(212, 175, 55, 0.2) !important;
}

section[data-testid="stSidebar"] .stButton > button:focus,
section[data-testid="stSidebar"] .stButton > button:active {
  background: rgba(212, 175, 55, 0.15) !important;
  border-color: var(--gold-primary) !important;
  border-left: 2px solid var(--gold-light) !important;
  color: var(--gold-light) !important;
}

/* Sidebar Footer Seal */
.sb-footer-seal {
  margin-top: 1.2rem;
  padding: 0.7rem 0.5rem;
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--t-muted);
  letter-spacing: 1px;
  text-align: center;
  border-top: 1px solid var(--gold-border-subtle);
  border-bottom: 1px solid var(--gold-border-subtle);
  background: rgba(212, 175, 55, 0.03);
}

.sb-footer-seal span {
  display: block;
}

.sb-footer-seal .seal-sub {
  font-size: 0.52rem;
  color: var(--gold-dim);
  margin-top: 2px;
  letter-spacing: 1.4px;
}

/* ═══════════════════════════════════════
   TOP BAR: Search, Location & Profile
   ═══════════════════════════════════════ */
.top-bar-location {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-surface);
  border: 1px solid var(--gold-border);
  padding: 6px 12px;
  border-radius: var(--radius);
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--gold-light);
  letter-spacing: 0.5px;
  white-space: nowrap;
  width: 100%;
  justify-content: center;
}

.top-bar-user {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 5px 12px 5px 10px;
  border-radius: var(--radius);
  background: linear-gradient(135deg, #161922 0%, #0d0e13 100%);
  border: 1px solid var(--gold-border);
  font-size: 0.74rem;
  color: var(--t-primary);
  font-weight: 600;
  letter-spacing: 0.4px;
  white-space: nowrap;
  width: 100%;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

.top-bar-user:hover {
  border-color: var(--gold-primary);
  box-shadow: 0 4px 14px rgba(0,0,0,0.6), 0 0 12px rgba(212, 175, 55, 0.22);
  transform: translateY(-1px);
}

.user-greeting-block {
  display: flex;
  flex-direction: column;
  line-height: 1.18;
  text-align: left;
}

.user-greeting-time {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--gold-primary);
  letter-spacing: 0.8px;
  text-transform: uppercase;
  font-weight: 700;
}

.user-greeting-name {
  font-family: var(--font-sans);
  font-size: 0.76rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.3px;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-bar-avatar {
  width: 30px;
  height: 30px;
  border-radius: 3px;
  background: linear-gradient(135deg, #2a220e 0%, #0d0e12 100%);
  border: 1px solid var(--gold-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--gold-light);
  box-shadow: 0 0 8px rgba(212, 175, 55, 0.2);
  flex-shrink: 0;
}

.hero-greeting-line {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--gold-light);
  letter-spacing: 0.5px;
  background: rgba(212, 175, 55, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.25);
  border-radius: 3px;
  padding: 3px 10px;
  margin-bottom: 6px;
}

.hero-greeting-dot {
  color: var(--gold-primary);
  font-size: 0.6rem;
}

/* Search Input Box */
.stTextInput > div > div > input {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--gold-border) !important;
  color: #ffffff !important;
  border-radius: var(--radius) !important;
  font-size: 0.82rem !important;
  padding: 0.55rem 1rem !important;
  letter-spacing: 0.3px !important;
  transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
  border-color: var(--gold-primary) !important;
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.2) !important;
  background-color: var(--bg-surface) !important;
}

.stTextInput > div > div > input::placeholder {
  color: var(--t-muted) !important;
  font-size: 0.78rem !important;
}

/* ═══════════════════════════════════════
   HERO BANNER — Animated Weather Chamber
   ═══════════════════════════════════════ */
.hero-banner {
  position: relative;
  background: radial-gradient(ellipse at 15% 50%, #15130b 0%, #08090c 70%);
  border: 1px solid var(--gold-border);
  border-left: 3px solid var(--gold-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  padding: 1.1rem 1.6rem;
  margin-bottom: 0.8rem;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 6px 20px rgba(0,0,0,0.7), var(--gold-glow);
}

/* Atmosphere layer container */
.hero-atmosphere-backdrop {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

/* ── 1. RAIN ANIMATION ── */
.hero-anim-rain {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  animation: thunderFlash 9s ease-in-out infinite;
}

.rain-drop {
  position: absolute;
  background: linear-gradient(180deg, transparent 0%, rgba(212, 175, 55, 0.5) 70%, rgba(255, 255, 255, 0.9) 100%);
  width: 1.5px;
  height: 28px;
  opacity: 0.65;
  animation: rainDropFall 0.8s linear infinite;
}

@keyframes rainDropFall {
  0% { transform: translateY(-40px) translateX(0); opacity: 0; }
  25% { opacity: 0.75; }
  100% { transform: translateY(160px) translateX(-30px); opacity: 0; }
}

@keyframes thunderFlash {
  0%, 89%, 93%, 100% { background: transparent; }
  90% { background: radial-gradient(ellipse at 70% 30%, rgba(212, 175, 55, 0.25) 0%, rgba(255,255,255,0.15) 30%, transparent 70%); }
}

/* ── 2. SUNNY ANIMATION ── */
.hero-anim-sunny {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
}

.sun-corona {
  position: absolute;
  top: -40px; right: 110px;
  width: 180px; height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.35) 0%, rgba(249, 233, 190, 0.15) 40%, transparent 70%);
  animation: sunPulse 4.5s ease-in-out infinite alternate;
}

.sun-rays {
  position: absolute;
  top: -80px; right: 70px;
  width: 260px; height: 260px;
  background: conic-gradient(from 0deg, 
    transparent 0deg 20deg, rgba(212,175,55,0.12) 20deg 40deg, 
    transparent 40deg 60deg, rgba(212,175,55,0.12) 60deg 80deg, 
    transparent 80deg 100deg, rgba(212,175,55,0.12) 100deg 120deg, 
    transparent 120deg 140deg, rgba(212,175,55,0.12) 140deg 160deg, 
    transparent 160deg 180deg, rgba(212,175,55,0.12) 180deg 200deg, 
    transparent 200deg 220deg, rgba(212,175,55,0.12) 220deg 240deg, 
    transparent 240deg 260deg, rgba(212,175,55,0.12) 260deg 280deg, 
    transparent 280deg 300deg, rgba(212,175,55,0.12) 300deg 320deg, 
    transparent 320deg 340deg, rgba(212,175,55,0.12) 340deg 360deg
  );
  border-radius: 50%;
  animation: sunRotate 35s linear infinite;
}

@keyframes sunPulse {
  0% { transform: scale(0.92); opacity: 0.3; }
  100% { transform: scale(1.15); opacity: 0.6; }
}

@keyframes sunRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ── 3. CLOUDY ANIMATION ── */
.hero-anim-cloudy {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
}

.cloud-mist-1 {
  position: absolute;
  width: 180%; height: 100%;
  top: 0; left: 0;
  background: radial-gradient(ellipse at 30% 60%, rgba(212, 175, 55, 0.08) 0%, transparent 45%),
              radial-gradient(ellipse at 75% 40%, rgba(180, 190, 205, 0.08) 0%, transparent 50%);
  animation: cloudDriftSlow 24s linear infinite alternate;
}

.cloud-mist-2 {
  position: absolute;
  width: 170%; height: 100%;
  top: 0; left: 0;
  background: radial-gradient(ellipse at 50% 70%, rgba(160, 170, 190, 0.07) 0%, transparent 40%),
              radial-gradient(ellipse at 15% 30%, rgba(212, 175, 55, 0.06) 0%, transparent 45%);
  animation: cloudDriftFast 16s linear infinite alternate;
}

@keyframes cloudDriftSlow {
  0% { transform: translateX(-25%); }
  100% { transform: translateX(5%); }
}

@keyframes cloudDriftFast {
  0% { transform: translateX(0%); }
  100% { transform: translateX(-20%); }
}

/* ── 4. COLD / SHIVERING ANIMATION ── */
.hero-anim-cold {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
}

.frost-crystal {
  position: absolute;
  width: 4px; height: 4px;
  border-radius: 50%;
  background: rgba(220, 240, 255, 0.85);
  box-shadow: 0 0 6px rgba(180, 220, 255, 0.9);
  animation: frostFallDrift 4s linear infinite, coldTremble 0.6s ease-in-out infinite alternate;
}

@keyframes frostFallDrift {
  0% { transform: translateY(-15px); opacity: 0; }
  25% { opacity: 0.9; }
  100% { transform: translateY(150px); opacity: 0; }
}

@keyframes coldTremble {
  0% { margin-left: -2px; }
  100% { margin-left: 2px; }
}

/* Hero Content Typography */
.hero-scope-badge {
  position: absolute;
  top: 10px;
  left: 18px;
  z-index: 2;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid var(--gold-dim);
  padding: 2px 8px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 1.2px;
  color: var(--gold-light);
  text-transform: uppercase;
}

.hero-content {
  position: relative;
  z-index: 2;
  padding-top: 10px;
}

.hero-title-bn {
  font-family: var(--font-bn) !important;
  font-size: 2.1rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.1;
  margin-bottom: 2px;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.8);
}

.hero-subtitle {
  font-family: var(--font-serif);
  font-size: 0.78rem;
  color: var(--gold-primary);
  font-weight: 600;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.hero-tagline-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.66rem;
  color: var(--t-secondary);
  letter-spacing: 0.5px;
}

.hero-tagline-divider {
  width: 3px;
  height: 3px;
  background: var(--gold-dim);
  transform: rotate(45deg);
}

.hero-weather-box {
  position: relative;
  z-index: 2;
  text-align: right;
  border: 1px solid var(--gold-border);
  background: rgba(8, 10, 14, 0.85);
  padding: 8px 14px;
  border-radius: var(--radius);
  backdrop-filter: blur(8px);
  min-width: 130px;
}

.hero-weather-temp {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--gold-light);
  line-height: 1;
}

.hero-weather-city {
  font-size: 0.72rem;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  margin-top: 2px;
}

.hero-weather-condition {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hero-datetime {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--t-muted);
  margin-top: 4px;
  text-align: right;
  letter-spacing: 0.4px;
}

/* ═══════════════════════════════════════
   PROFESSIONAL NEWS CARDS & GRID
   ═══════════════════════════════════════ */
.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 16px;
  margin: 16px 0 24px 0;
  width: 100%;
}

.news-card {
  background: linear-gradient(145deg, #11141a 0%, #0a0c10 100%);
  border: 1px solid var(--gold-border);
  border-left: 3px solid var(--gold-primary);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 18px rgba(0,0,0,0.5), 0 0 10px rgba(212, 175, 55, 0.05);
  position: relative;
  overflow: hidden;
}

.news-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 50px;
  height: 50px;
  background: radial-gradient(circle at top right, rgba(212, 175, 55, 0.12), transparent 70%);
  pointer-events: none;
}

.news-card:hover {
  transform: translateY(-3px);
  border-color: var(--gold-primary);
  box-shadow: 0 8px 25px rgba(0,0,0,0.7), 0 0 20px rgba(212, 175, 55, 0.25);
  background: linear-gradient(145deg, #161b24 0%, #0d0f14 100%);
}

.news-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
  padding-bottom: 6px;
}

.news-card-source {
  font-family: var(--font-serif);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.news-card-time {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--t-muted);
}

.news-card-title {
  margin: 6px 0 8px 0;
  line-height: 1.35;
}

.news-card-title a {
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffffff !important;
  text-decoration: none !important;
  transition: color 0.15s ease;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-card-title a:hover {
  color: var(--gold-light) !important;
  text-decoration: underline !important;
}

.news-card-summary {
  font-size: 0.8rem;
  color: var(--t-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-card-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.news-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid rgba(212, 175, 55, 0.12);
  margin-top: auto;
}

.read-story-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid var(--gold-primary);
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--gold-light) !important;
  text-decoration: none !important;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  transition: all 0.2s ease;
}

.read-story-btn:hover {
  background: var(--gold-primary);
  color: #000000 !important;
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.5);
  transform: translateY(-1px);
}

/* ═══════════════════════════════════════
   CATEGORY TABS — High-Density Royal Pills
   ═══════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  border-bottom: 1px solid var(--gold-border-subtle) !important;
  gap: 5px !important;
  overflow-x: auto !important;
  flex-wrap: nowrap !important;
  padding-bottom: 6px !important;
  margin-bottom: 0.5rem !important;
}

.stTabs [data-baseweb="tab"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--t-secondary) !important;
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase !important;
  padding: 4px 11px !important;
  white-space: nowrap !important;
  transition: all 0.15s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
  border-color: var(--gold-primary) !important;
  color: var(--gold-light) !important;
  background: var(--gold-soft-bg) !important;
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0.05) 100%) !important;
  border-color: var(--gold-primary) !important;
  color: var(--gold-light) !important;
  font-weight: 700 !important;
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.15) !important;
}

.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ═══════════════════════════════════════
   SECTION HEADERS
   ═══════════════════════════════════════ */
.section-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.7rem 0 0.4rem;
  border-bottom: 1px solid var(--gold-border-subtle);
  padding-bottom: 4px;
}

.section-hdr-title {
  font-family: var(--font-serif);
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-hdr-box {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--gold-primary);
  transform: rotate(45deg);
}

.section-hdr-sub {
  font-family: var(--font-sans);
  font-size: 0.66rem;
  color: var(--t-muted);
  font-weight: 400;
  letter-spacing: 0.2px;
  margin-left: 8px;
}

.view-all-link {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--gold-primary);
  font-weight: 600;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  text-decoration: none;
  border: 1px solid var(--gold-border);
  padding: 2px 6px;
  border-radius: 2px;
  transition: all 0.15s ease;
}

.view-all-link:hover {
  background: var(--gold-soft-bg);
  border-color: var(--gold-primary);
  color: var(--gold-light);
}

/* ═══════════════════════════════════════
   STORY #1 — Featured Lead Intelligence (Compact)
   ═══════════════════════════════════════ */
.featured-story {
  display: flex;
  gap: 1.2rem;
  background: var(--bg-card);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 0.6rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  transition: all 0.2s ease;
}

.featured-story:hover {
  border-color: var(--gold-border-bright);
  box-shadow: 0 6px 20px rgba(0,0,0,0.7), var(--gold-glow);
}

.featured-img {
  width: 200px;
  min-height: 130px;
  background: linear-gradient(135deg, #18150c 0%, #0a0b0e 100%);
  border-right: 1px solid var(--gold-border-subtle);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 0.8rem;
  text-align: center;
}

.featured-watermark {
  border: 1px solid var(--gold-dim);
  padding: 6px 10px;
  border-radius: 2px;
  text-align: center;
}

.featured-watermark-top {
  font-family: var(--font-serif);
  font-size: 0.64rem;
  font-weight: 700;
  color: var(--gold-primary);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.featured-watermark-sub {
  font-family: var(--font-mono);
  font-size: 0.54rem;
  color: var(--t-muted);
  letter-spacing: 0.8px;
  margin-top: 2px;
}

.featured-body {
  padding: 0.8rem 1rem 0.8rem 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.featured-badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.featured-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #090a0d;
  border: 1px solid var(--gold-primary);
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--gold-primary);
  flex-shrink: 0;
}

.royal-box-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  border: 1px solid var(--gold-border);
  background: var(--gold-soft-bg);
  color: var(--gold-light);
}

.featured-headline {
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.featured-headline a {
  color: #ffffff;
  text-decoration: none;
  transition: color 0.15s ease;
}

.featured-headline a:hover {
  color: var(--gold-light);
}

.featured-summary {
  font-size: 0.78rem;
  color: var(--t-secondary);
  line-height: 1.45;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.featured-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.68rem;
  color: var(--t-muted);
  flex-wrap: wrap;
}

.featured-meta-source {
  font-weight: 700;
  color: var(--gold-primary);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.featured-meta-sep {
  color: var(--gold-dim);
}

/* ═══════════════════════════════════════
   COMPACT STORY ROWS (#2-#5)
   ═══════════════════════════════════════ */
.story-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 12px;
  border: 1px solid var(--gold-border-subtle);
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  background: var(--bg-card);
  transition: all 0.15s ease;
}

.story-row:hover {
  background: var(--bg-card-hover);
  border-color: var(--gold-border);
  box-shadow: 0 2px 10px rgba(0,0,0,0.5);
}

.story-rank {
  width: 20px;
  height: 20px;
  border-radius: 2px;
  background: #08090c;
  border: 1px solid var(--gold-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 0.66rem;
  font-weight: 700;
  color: var(--gold-dim);
  flex-shrink: 0;
}

.story-content {
  flex: 1;
  min-width: 0;
}

.story-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--t-primary);
  margin-bottom: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.story-title a {
  color: var(--t-primary);
  text-decoration: none;
  transition: color 0.15s ease;
}

.story-title a:hover {
  color: var(--gold-light);
}

.story-excerpt {
  font-size: 0.7rem;
  color: var(--t-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.story-meta-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  flex-shrink: 0;
  min-width: 100px;
}

.story-source-time {
  font-size: 0.64rem;
  color: var(--t-muted);
  font-family: var(--font-mono);
}

.story-source-name {
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.story-location {
  font-size: 0.6rem;
  color: var(--gold-dim);
  font-family: var(--font-mono);
  text-transform: uppercase;
}

.relevance-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 700;
  min-width: 38px;
  border: 1px solid var(--gold-border);
  background: rgba(212, 175, 55, 0.08);
  color: var(--gold-light);
}

/* ═══════════════════════════════════════
   RIGHT PANEL — Compact Dossier
   ═══════════════════════════════════════ */
.rp-card {
  background: var(--bg-card);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius);
  padding: 0.8rem 0.9rem;
  margin-bottom: 0.6rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              border-color 0.25s ease,
              box-shadow 0.25s ease,
              background 0.25s ease;
}

.rp-card:hover {
  transform: translateY(-2px);
  border-color: rgba(212, 175, 55, 0.65);
  box-shadow: 0 8px 25px rgba(0,0,0,0.7), 0 0 16px rgba(212, 175, 55, 0.22);
  background: linear-gradient(180deg, #131722 0%, #0d0f14 100%);
}

.rp-card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.6rem;
  font-family: var(--font-serif);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  color: var(--gold-light);
  text-transform: uppercase;
  border-bottom: 1px solid var(--gold-border-subtle);
  padding-bottom: 4px;
}

.rp-card-action {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--gold-primary);
  font-weight: 600;
  letter-spacing: 0.8px;
  cursor: pointer;
  border: 1px solid var(--gold-border);
  padding: 1px 5px;
  border-radius: 2px;
  transition: all 0.15s ease;
}

.rp-card-action:hover {
  background: var(--gold-soft-bg);
  border-color: var(--gold-primary);
  color: #ffffff;
}

/* Local News Widget */
.local-news-card {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.local-news-card:hover {
  background: rgba(212, 175, 55, 0.06);
  border-color: rgba(212, 175, 55, 0.3);
  transform: translateX(3px);
}

.local-news-box {
  width: 48px;
  height: 48px;
  border-radius: 3px;
  border: 1px solid var(--gold-border);
  background: linear-gradient(135deg, #1a1710 0%, #0a0b0e 100%);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: all 0.2s ease;
}

.local-news-card:hover .local-news-box {
  border-color: var(--gold-primary);
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.35);
  transform: scale(1.05);
}

.local-news-box-tag {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 700;
  color: var(--gold-primary);
  letter-spacing: 0.8px;
}

.local-news-city {
  font-size: 0.84rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.4px;
}

.local-news-desc {
  font-size: 0.66rem;
  color: var(--t-muted);
  margin-top: 1px;
}

.location-access-box {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 1px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  background: rgba(34, 197, 94, 0.08);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.25);
  margin-top: 4px;
  text-transform: uppercase;
}

/* Trending Topics */
.trending-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.trend-pill {
  padding: 4px 9px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.64rem;
  font-weight: 600;
  background: var(--bg-surface);
  border: 1px solid var(--gold-border-subtle);
  color: var(--t-secondary);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  display: inline-block;
}

.trend-pill:hover {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.3) 0%, rgba(212, 175, 55, 0.12) 100%);
  border-color: var(--gold-primary);
  color: #ffffff;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.5), 0 0 10px rgba(212, 175, 55, 0.3);
}

/* Quick Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.stat-cell {
  background: var(--bg-surface);
  border: 1px solid var(--gold-border-subtle);
  border-radius: var(--radius-sm);
  padding: 7px 8px;
  text-align: center;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: default;
}

.stat-cell:hover {
  border-color: var(--gold-primary);
  background: linear-gradient(180deg, #171b26 0%, #101218 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.6), 0 0 10px rgba(212, 175, 55, 0.18);
}

.stat-cell:hover .stat-value {
  color: #ffffff;
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.6);
}

.stat-value {
  font-family: var(--font-serif);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--gold-light);
  line-height: 1;
  transition: color 0.2s ease;
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--t-muted);
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.stat-change {
  font-family: var(--font-mono);
  font-size: 0.54rem;
  color: var(--accent-green);
  margin-top: 2px;
  font-weight: 600;
}

/* Intelligence Promo Box */
.ai-promo {
  background: radial-gradient(ellipse at center, #18150c 0%, #090a0d 100%);
  border: 1px solid var(--gold-primary);
  border-radius: var(--radius);
  padding: 0.9rem;
  text-align: center;
  margin-bottom: 0.6rem;
  box-shadow: var(--gold-glow);
  transition: all 0.25s ease;
}

.ai-promo:hover {
  transform: translateY(-2px);
  border-color: var(--gold-light);
  box-shadow: 0 8px 30px rgba(0,0,0,0.8), 0 0 24px rgba(212, 175, 55, 0.35);
}

.ai-promo-crest {
  display: inline-block;
  font-family: var(--font-serif);
  font-size: 0.64rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: var(--gold-primary);
  border: 1px solid var(--gold-dim);
  padding: 2px 7px;
  border-radius: 2px;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.ai-promo-title {
  font-family: var(--font-serif);
  font-size: 0.84rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 4px;
  letter-spacing: 0.4px;
}

.ai-promo-desc {
  font-size: 0.68rem;
  color: var(--t-secondary);
  line-height: 1.4;
  margin-bottom: 8px;
}

.ai-promo-btn {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  background: rgba(212, 175, 55, 0.12);
  border: 1px solid var(--gold-primary);
  color: var(--gold-light);
  text-decoration: none;
  text-transform: uppercase;
  transition: all 0.15s ease;
}

.ai-promo-btn:hover {
  background: rgba(212, 175, 55, 0.3);
  box-shadow: var(--gold-glow);
  color: #ffffff;
}

/* ═══════════════════════════════════════
   GLOBAL STREAMLIT WIDGETS
   ═══════════════════════════════════════ */
.stButton > button,
button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
  background: var(--bg-card) !important;
  color: var(--gold-light) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase !important;
  padding: 0.4rem 0.8rem !important;
  transition: all 0.15s ease !important;
}

.stButton > button:hover,
button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
  background: var(--gold-soft-bg) !important;
  color: #ffffff !important;
  border-color: var(--gold-primary) !important;
  box-shadow: var(--gold-glow) !important;
}

section[data-testid="stSidebar"] .stButton > button {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
  border-left: 2px solid transparent !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
  transform: translateX(4px) !important;
  border-left: 2px solid var(--gold-primary) !important;
  background: linear-gradient(90deg, rgba(212, 175, 55, 0.16) 0%, rgba(212, 175, 55, 0.04) 100%) !important;
  color: var(--gold-light) !important;
  border-color: var(--gold-primary) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.4), var(--gold-glow) !important;
}

.stAlert {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--gold-border) !important;
  background: var(--bg-card) !important;
  color: var(--t-primary) !important;
}

.stSelectbox > div > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: var(--radius-sm) !important;
  color: #ffffff !important;
}

.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--gold-light) !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.4px !important;
}

@media (max-width: 900px) {
  .featured-story { flex-direction: column; }
  .featured-img { width: 100%; min-height: 110px; }
  .featured-body { padding: 0.8rem; }
  .hero-banner { flex-direction: column; gap: 12px; align-items: flex-start; }
  .hero-weather-box { text-align: left; }
}

/* ═══════════════════════════════════════
   3D BOOK OPENING & FOLDING EFFECT
   ═══════════════════════════════════════ */
@keyframes bookOpen3D {
  0% {
    transform: perspective(1400px) rotateY(-85deg);
    transform-origin: right center;
    opacity: 0.1;
    filter: brightness(0.6);
  }
  60% {
    transform: perspective(1400px) rotateY(-12deg);
    opacity: 0.95;
    filter: brightness(1.08);
  }
  100% {
    transform: perspective(1400px) rotateY(0deg);
    transform-origin: right center;
    opacity: 1;
    filter: brightness(1);
  }
}

.book-panel-wrapper {
  position: relative;
  animation: bookOpen3D 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  transform-style: preserve-3d;
  background: radial-gradient(ellipse at 90% 10%, #151822 0%, #0c0e14 100%);
  border: 1px solid var(--gold-border);
  border-left: 3px solid var(--gold-primary);
  border-radius: var(--radius);
  padding: 0.8rem 0.8rem 0.4rem;
  box-shadow: -15px 0 35px rgba(0,0,0,0.8), 0 0 20px rgba(212, 175, 55, 0.16);
  margin-bottom: 1rem;
}

.book-spine-crease {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #d4af37 0%, #f3e5ab 50%, #8c6d23 100%);
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
  border-radius: 2px 0 0 2px;
}

.panel-section-tag {
  font-family: var(--font-serif);
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 1.2px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 2px;
}

/* ═══════════════════════════════════════
   MOBILE NAVIGATION DRAWER & CONTROLS
   ═══════════════════════════════════════ */
@keyframes mobileDrawerSlide {
  0% {
    opacity: 0;
    transform: translateY(-12px) scale(0.98);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.mobile-menu-drawer {
  background: radial-gradient(ellipse at 50% 0%, #171b24 0%, #090a0e 100%) !important;
  border: 1.5px solid var(--gold-primary) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: 0 16px 50px rgba(0,0,0,0.92), 0 0 30px rgba(212, 175, 55, 0.22) !important;
  padding: 1rem 0.9rem !important;
  margin-bottom: 1.2rem !important;
  animation: mobileDrawerSlide 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
  position: relative !important;
  z-index: 99999 !important;
}

.mobile-menu-header {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding-bottom: 0.6rem !important;
  border-bottom: 1px solid var(--gold-border) !important;
  margin-bottom: 0.8rem !important;
}

.mobile-menu-title {
  font-family: var(--font-serif) !important;
  font-size: 0.85rem !important;
  font-weight: 800 !important;
  color: var(--gold-light) !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
}

.mobile-menu-badge {
  font-family: var(--font-mono) !important;
  font-size: 0.62rem !important;
  color: var(--gold-primary) !important;
  background: rgba(212, 175, 55, 0.12) !important;
  border: 1px solid var(--gold-border) !important;
  padding: 2px 7px !important;
  border-radius: 3px !important;
  letter-spacing: 0.5px !important;
}

.mobile-menu-hint {
  font-size: 0.72rem !important;
  color: var(--t-secondary) !important;
  letter-spacing: 0.3px !important;
  margin-bottom: 0.65rem !important;
}

.mobile-nav-active-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(212, 175, 55, 0.15);
  border: 1px solid var(--gold-primary);
  color: var(--gold-light);
  padding: 3px 8px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
}

/* ═══════════════════════════════════════
   RESPONSIVE MEDIA QUERIES (MOBILE VIEW)
   ═══════════════════════════════════════ */
@media (max-width: 768px) {
  /* Layout & Padding */
  .block-container {
    padding-top: 0.3rem !important;
    padding-bottom: 1.8rem !important;
    padding-left: 0.65rem !important;
    padding-right: 0.65rem !important;
  }

  /* Sidebar behavior on mobile — overlay rather than pushing page */
  section[data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    width: 82vw !important;
    max-width: 310px !important;
    min-width: 260px !important;
    z-index: 9999999 !important;
    box-shadow: 20px 0 60px rgba(0,0,0,0.98), 0 0 30px rgba(212, 175, 55, 0.4) !important;
  }

  /* Top Bar layout on mobile */
  .top-bar-location {
    font-size: 0.72rem !important;
    padding: 0.3rem 0.5rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .user-greeting-block {
    display: none !important;
  }

  .top-bar-avatar {
    width: 28px !important;
    height: 28px !important;
    font-size: 0.75rem !important;
  }

  /* Hero Banner mobile adaptation */
  .hero-banner {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 1rem !important;
    padding: 1.1rem 0.9rem !important;
  }

  .hero-title-bn {
    font-size: 2rem !important;
    letter-spacing: 0.5px !important;
  }

  .hero-subtitle {
    font-size: 0.62rem !important;
    letter-spacing: 1.4px !important;
  }

  .hero-tagline-row {
    flex-wrap: wrap !important;
    gap: 6px !important;
    font-size: 0.58rem !important;
  }

  .hero-weather-box {
    width: 100% !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-top: 0.4rem !important;
  }

  .hero-weather-temp {
    font-size: 1.5rem !important;
  }

  .hero-datetime {
    font-size: 0.65rem !important;
    margin-top: 4px !important;
  }

  /* Featured Story Card mobile adaptation */
  .featured-story {
    flex-direction: column !important;
    border-radius: var(--radius) !important;
  }

  .featured-img {
    width: 100% !important;
    min-height: 140px !important;
    max-height: 170px !important;
  }

  .featured-body {
    padding: 0.85rem !important;
  }

  .featured-headline {
    font-size: 1.08rem !important;
    line-height: 1.35 !important;
  }

  .featured-summary {
    font-size: 0.8rem !important;
    line-height: 1.45 !important;
    max-height: 4.8em !important;
  }

  /* Story Rows mobile adaptation */
  .story-row {
    flex-wrap: wrap !important;
    gap: 8px !important;
    padding: 0.7rem 0.65rem !important;
  }

  .story-content {
    width: calc(100% - 50px) !important;
  }

  .story-title {
    font-size: 0.88rem !important;
  }

  .story-excerpt {
    font-size: 0.76rem !important;
  }

  .story-meta-right {
    width: 100% !important;
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between !important;
    align-items: center !important;
    border-top: 1px dashed var(--gold-border-subtle) !important;
    padding-top: 5px !important;
    margin-top: 3px !important;
  }

  .relevance-box {
    align-self: flex-start !important;
  }

  /* News Card Grid mobile */
  .news-grid {
    grid-template-columns: 1fr !important;
    gap: 0.85rem !important;
  }

  .news-card {
    min-height: auto !important;
    padding: 0.85rem !important;
  }

  .news-card-title {
    font-size: 0.95rem !important;
  }

  /* Tabs horizontal scrolling */
  div[data-baseweb="tab-list"] {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
  }

  button[data-baseweb="tab"] {
    padding: 5px 9px !important;
    font-size: 0.72rem !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
  }

  /* Stats Grid */
  .stats-grid {
    grid-template-columns: 1fr 1fr !important;
    gap: 0.5rem !important;
  }

  /* Section header on mobile */
  .section-hdr {
    flex-wrap: wrap !important;
    gap: 4px !important;
  }

  .section-hdr-title {
    font-size: 0.82rem !important;
  }

  .view-all-link {
    font-size: 0.65rem !important;
  }
}

</style>
<script>
// Auto-close sidebar on menu option click and add UX polish
(function() {
  function attachSidebarNavListener() {
    try {
      const parentDoc = window.parent.document;
      if (!parentDoc) return;
      const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
      if (!sidebar) return;

      const buttons = sidebar.querySelectorAll('button');
      buttons.forEach(btn => {
        if (btn.dataset.autocloseAttached) return;
        btn.dataset.autocloseAttached = "true";
        // Do not trigger auto-collapse on the close cross button itself
        if (btn.closest('[data-testid="stSidebarCollapseButton"]')) return;
        if (btn.innerText && btn.innerText.trim() === '✕') return;

        btn.addEventListener('click', function() {
          // Wait 120ms so Streamlit receives the selection, then fold sidebar
          setTimeout(function() {
            const collapseBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"] button')
              || parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]')
              || parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]');
            if (collapseBtn) {
              collapseBtn.click();
            }
          }, 120);
        });
      });
    } catch(e) {}
  }

  setInterval(attachSidebarNavListener, 400);
})();
</script>
"""


def get_geo_script_html():
    """HTML component that requests HTML5 browser geolocation cleanly."""
    return """
<div id="geo-box" style="display:none;"></div>
<script>
(function() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function(pos) {
        var payload = {
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          status: 'granted'
        };
        window.parent.postMessage({
          type: 'streamlit:setComponentValue',
          value: payload
        }, '*');
      },
      function(err) {
        var payload = {
          lat: null,
          lon: null,
          status: 'denied',
          error: err.message
        };
        window.parent.postMessage({
          type: 'streamlit:setComponentValue',
          value: payload
        }, '*');
      },
      { timeout: 8000, maximumAge: 300000 }
    );
  } else {
    window.parent.postMessage({
      type: 'streamlit:setComponentValue',
      value: { lat: null, lon: null, status: 'unsupported' }
    }, '*');
  }
})();
</script>
"""
