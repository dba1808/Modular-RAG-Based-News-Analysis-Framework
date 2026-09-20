"""
Authentication Module — ত্রিকোণদৃষ্টি (TrikonDrishti)
═══════════════════════════════════════════════════════
Provides login/signup gating using streamlit-authenticator.
Credentials are stored in users.yaml with bcrypt-hashed passwords.
"""

import json
import yaml
import bcrypt
import hashlib
import streamlit as st
from pathlib import Path
from datetime import datetime

USERS_FILE = Path(__file__).parent / "users.yaml"
SESSION_FILE = Path(__file__).parent / "active_session.json"


def _load_users() -> dict:
    """Load users from YAML file."""
    if not USERS_FILE.exists():
        return {"users": {}}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def _save_users(data: dict):
    """Save users to YAML file."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def _load_session() -> dict:
    """Load persistent session from disk."""
    if not SESSION_FILE.exists():
        return {}
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_session(data: dict):
    """Save persistent session to disk."""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _clear_session():
    """Clear persistent session from disk."""
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
    except Exception:
        pass


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def is_authenticated() -> bool:
    """Check if a user is currently logged in, with persistent session across page reloads."""
    if st.session_state.get("authenticated", False):
        return True

    # Check query params or persistent local session
    active = _load_session()
    if active and active.get("profile"):
        token = active.get("token")
        profile = active.get("profile", {})
        
        # Verify query param if present
        param_token = None
        try:
            param_token = st.query_params.get("session")
        except Exception:
            pass

        if not param_token or param_token == token:
            st.session_state.authenticated = True
            st.session_state.user_profile = profile
            try:
                st.query_params["session"] = token
            except Exception:
                pass
            return True

    return False


def get_current_user() -> dict:
    """Return the current logged-in user's profile."""
    return st.session_state.get("user_profile", {})


def logout():
    """Log out the current user and wipe session."""
    st.session_state.authenticated = False
    st.session_state.user_profile = {}
    _clear_session()
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


def _do_login(username: str, password: str) -> bool:
    """Validate credentials and set persistent session on success."""
    data = _load_users()
    users = data.get("users", {})
    user = users.get(username)
    if user and _verify_password(password, user.get("password", "")):
        profile = {
            "username": username,
            "name": user.get("name", username),
            "email": user.get("email", ""),
            "role": user.get("role", "reader"),
            "joined": user.get("joined", ""),
        }
        token = hashlib.sha256(f"{username}:{datetime.now().isoformat()}".encode()).hexdigest()[:24]
        
        st.session_state.authenticated = True
        st.session_state.user_profile = profile
        
        _save_session({
            "token": token,
            "username": username,
            "profile": profile,
            "logged_in_at": datetime.now().isoformat(),
        })
        
        try:
            st.query_params["session"] = token
        except Exception:
            pass
        return True
    return False


def get_time_greeting() -> str:
    """Return an elegant, time-of-day greeting (e.g., 'Good morning', 'Good afternoon', 'Good evening')."""
    h = datetime.now().hour
    if 5 <= h < 12:
        return "Good morning"
    elif 12 <= h < 17:
        return "Good afternoon"
    elif 17 <= h < 21:
        return "Good evening"
    else:
        return "Good night"


def _do_register(username: str, password: str, name: str, email: str) -> tuple:
    """Register a new user, log them in immediately, and set persistent session."""
    u = username.strip().lower()
    if len(u) < 3:
        return False, "Username must be at least 3 characters.", {}
    if len(password) < 4:
        return False, "Password must be at least 4 characters.", {}

    data = _load_users()
    users = data.get("users", {})

    if u in users:
        return False, "Username already exists. Please choose another or sign in.", {}

    full_name = name.strip() if name.strip() else u.capitalize()

    profile = {
        "username": u,
        "name": full_name,
        "email": email.strip(),
        "role": "reader",
        "joined": datetime.now().isoformat(),
    }

    users[u] = {
        "name": full_name,
        "email": email.strip(),
        "password": _hash_password(password),
        "role": "reader",
        "joined": profile["joined"],
    }
    data["users"] = users
    _save_users(data)

    # Immediately authenticate and create persistent session
    token = hashlib.sha256(f"{u}:{datetime.now().isoformat()}".encode()).hexdigest()[:24]
    st.session_state.authenticated = True
    st.session_state.user_profile = profile
    _save_session({
        "token": token,
        "username": u,
        "profile": profile,
        "logged_in_at": datetime.now().isoformat(),
    })
    try:
        st.query_params["session"] = token
    except Exception:
        pass

    return True, "Account created successfully!", profile


def render_auth_page():
    """Render the full-page login/signup interface."""

    # Auth page styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Hind+Siliguri:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

    section[data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none !important; }

    .auth-brand-header {
        text-align: center;
        margin: 2.2rem auto 1.2rem;
    }
    .auth-brand-icon {
        width: 52px;
        height: 52px;
        background: linear-gradient(135deg, #221c0e 0%, #0a0c10 100%);
        border: 1px solid #d4af37;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: 'Cinzel', serif;
        font-size: 1.15rem;
        font-weight: 800;
        color: #d4af37;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.25);
    }
    .auth-brand-name {
        font-family: 'Hind Siliguri', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.8);
    }
    .auth-brand-sub {
        font-family: 'Cinzel', serif;
        font-size: 0.72rem;
        color: #d4af37;
        margin-top: 6px;
        letter-spacing: 1.8px;
        text-transform: uppercase;
    }
    .auth-welcome-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 12px;
        border-radius: 20px;
        background: rgba(212, 175, 55, 0.1);
        border: 1px solid rgba(212, 175, 55, 0.3);
        color: #e6c65c;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.8px;
        margin-top: 10px;
        text-transform: uppercase;
    }
    .auth-footer {
        text-align: center;
        font-size: 0.72rem;
        color: #78736a;
        margin-top: 2rem;
        line-height: 1.6;
        letter-spacing: 0.4px;
    }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.8, 1])

    with col_c:
        greeting_now = get_time_greeting()
        st.markdown(f"""
        <div class="auth-brand-header">
            <div class="auth-brand-icon">TD</div>
            <div class="auth-brand-name">ত্রিকোণদৃষ্টি</div>
            <div class="auth-brand-sub">TrikonDrishti · News Intelligence Dossier</div>
            <div class="auth-welcome-pill">✦ {greeting_now} · Secure Access Portal</div>
        </div>
        """, unsafe_allow_html=True)

        login_tab, signup_tab = st.tabs(["SIGN IN", "CREATE ACCOUNT"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("<p style='font-size:0.8rem;color:#b8b4a8;margin-bottom:0.8rem;letter-spacing:0.4px;'>Access your personalized regional intelligence dossier.</p>", unsafe_allow_html=True)
                login_user = st.text_input("Username", placeholder="Enter your username", key="login_user")
                login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
                login_submit = st.form_submit_button("Sign In to Dossier", use_container_width=True)

                if login_submit:
                    if login_user.strip() and login_pass.strip():
                        if _do_login(login_user.strip().lower(), login_pass.strip()):
                            greeting = get_time_greeting()
                            user_display = st.session_state.user_profile.get("name") or login_user.strip()
                            st.session_state.welcome_notice = f"{greeting}, {user_display}"
                            st.toast(f"✦ {greeting}, {user_display}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify your username and password.")
                    else:
                        st.warning("Please enter both username and password.")

        with signup_tab:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("<p style='font-size:0.8rem;color:#b8b4a8;margin-bottom:0.8rem;letter-spacing:0.4px;'>Register a profile to receive personalized daily briefings.</p>", unsafe_allow_html=True)
                reg_name = st.text_input("Full Name", placeholder="e.g. Debayudh Bhattacharya", key="reg_name", help="Your full name will be used in your personalized greetings")
                reg_email = st.text_input("Email Address", placeholder="name@domain.com", key="reg_email")
                reg_user = st.text_input("Username / Handle", placeholder="Choose handle (min 3 chars)", key="reg_user")
                reg_pass = st.text_input("Password", type="password", placeholder="Choose password (min 4 chars)", key="reg_pass")
                reg_submit = st.form_submit_button("Create Account & Access Dossier", use_container_width=True)

                if reg_submit:
                    if not reg_name.strip():
                        st.warning("Please enter your Full Name.")
                    elif not reg_user.strip() or not reg_pass.strip():
                        st.warning("Please enter both a username and password.")
                    else:
                        success, msg, profile = _do_register(
                            username=reg_user.strip(),
                            password=reg_pass.strip(),
                            name=reg_name.strip(),
                            email=reg_email.strip(),
                        )
                        if success:
                            greeting = get_time_greeting()
                            user_display = profile.get("name") or reg_name.strip()
                            st.session_state.welcome_notice = f"{greeting}, {user_display}"
                            st.toast(f"✦ {greeting}, {user_display}! Profile created.")
                            st.rerun()
                        else:
                            st.error(msg)

        st.markdown("""
        <div class="auth-footer">
            সঠিক খবর · পক্ষীয় বিশ্লেষণ · আপনার দৃষ্টিকোণ<br>
            তালে খবর — শুধু তথ্য নয়, এটা একটা দৃষ্টিভঙ্গি।
        </div>
        """, unsafe_allow_html=True)

