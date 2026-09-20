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
from typing import Optional, Dict, Any, Tuple

USERS_FILE = Path(__file__).parent / "users.yaml"


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


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


AUTH_COOKIE_NAME = "trikondrishti_auth"
_AUTH_SECRET_FILE = Path(__file__).parent / ".auth_secret"


def _get_auth_secret() -> str:
    """Get or generate a persistent secret key for signing session tokens."""
    if _AUTH_SECRET_FILE.exists():
        try:
            with open(_AUTH_SECRET_FILE, "r", encoding="utf-8") as f:
                sec = f.read().strip()
                if sec:
                    return sec
        except Exception:
            pass
    # Generate and store a strong secret key
    import secrets
    sec = secrets.token_urlsafe(32)
    try:
        with open(_AUTH_SECRET_FILE, "w", encoding="utf-8") as f:
            f.write(sec)
    except Exception:
        pass
    return sec


def _create_auth_token(username: str, expiry_days: float = 14.0) -> str:
    """Generate a cryptographically signed JWT session token."""
    import jwt
    from datetime import timezone, timedelta
    secret = _get_auth_secret()
    now_utc = datetime.now(timezone.utc)
    payload = {
        "sub": username.lower().strip(),
        "iat": int(now_utc.timestamp()),
        "exp": int((now_utc + timedelta(days=expiry_days)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _verify_auth_token(token: str) -> Optional[str]:
    """Verify and decode a signed JWT session token, returning username if valid."""
    if not token or not isinstance(token, str):
        return None
    import jwt
    secret = _get_auth_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None


def _get_browser_cookie_token() -> Optional[str]:
    """Inspect client HTTP cookies for an existing authenticated session token."""
    # 1. Check Streamlit native incoming HTTP cookies
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            raw = st.context.cookies.get(AUTH_COOKIE_NAME)
            if raw:
                return str(raw).strip()
    except Exception:
        pass

    # 2. Check CookieManager fallback
    try:
        import extra_streamlit_components as stx
        cm = stx.CookieManager(key="auth_cm_reader")
        raw = cm.get(AUTH_COOKIE_NAME)
        if raw:
            return str(raw).strip()
    except Exception:
        pass

    return None


def _set_browser_cookie(username: str):
    """Store the signed session token in the user's browser cookie."""
    if not username:
        return
    token = _create_auth_token(username)
    from datetime import timedelta

    # 1. Set via extra_streamlit_components
    try:
        import extra_streamlit_components as stx
        cm = stx.CookieManager(key="auth_cm_setter")
        cm.set(
            AUTH_COOKIE_NAME,
            token,
            expires_at=datetime.now() + timedelta(days=14),
            same_site="lax",
        )
    except Exception:
        pass

    # 2. Set via client-side cookie header script for instant availability
    try:
        import streamlit.components.v1 as components
        max_age = int(14 * 86400)
        js = f"""
        <script>
        try {{
          window.parent.document.cookie = "{AUTH_COOKIE_NAME}={token}; path=/; max-age={max_age}; SameSite=Lax;";
        }} catch(e) {{}}
        try {{
          document.cookie = "{AUTH_COOKIE_NAME}={token}; path=/; max-age={max_age}; SameSite=Lax;";
        }} catch(e) {{}}
        </script>
        """
        components.html(js, height=0, scrolling=False)
    except Exception:
        pass


def sync_auth_cookie(username: str):
    """Public helper to keep the client cookie in sync with the active session."""
    _set_browser_cookie(username)


def _delete_browser_cookie():
    """Wipe the authentication cookie from client browser."""
    # 1. Delete via CookieManager
    try:
        import extra_streamlit_components as stx
        cm = stx.CookieManager(key="auth_cm_deleter")
        cm.delete(AUTH_COOKIE_NAME)
    except Exception:
        pass

    # 2. Delete via JavaScript cookie expiration
    try:
        import streamlit.components.v1 as components
        js = f"""
        <script>
        try {{
          window.parent.document.cookie = "{AUTH_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0;";
        }} catch(e) {{}}
        try {{
          document.cookie = "{AUTH_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0;";
        }} catch(e) {{}}
        </script>
        """
        components.html(js, height=0, scrolling=False)
    except Exception:
        pass


def is_authenticated() -> bool:
    """
    Check if a user is currently logged in.
    1. Checks active session state.
    2. If user explicitly logged out in this browser session, respect it.
    3. If session state is empty (e.g. browser page refresh), seamlessly
       re-authenticates from the client browser's signed session cookie.
    4. Guarantees no identity leakage across separate browsers/devices.
    """
    if st.session_state.get("logged_out", False):
        return False

    # Fast path: already active in this WebSocket session
    if st.session_state.get("authenticated", False) and st.session_state.get("user_profile"):
        return True

    # Re-authentication path on browser refresh
    token = _get_browser_cookie_token()
    if token:
        valid_username = _verify_auth_token(token)
        if valid_username:
            users_data = _load_users().get("users", {})
            user_entry = users_data.get(valid_username)
            if user_entry:
                profile = {
                    "username": valid_username,
                    "name": user_entry.get("name") or valid_username,
                    "email": user_entry.get("email", ""),
                    "role": user_entry.get("role", "reader"),
                    "joined": user_entry.get("joined", ""),
                }
                st.session_state.authenticated = True
                st.session_state.user_profile = profile
                return True

    return False


def get_current_user() -> dict:
    """Return the current logged-in user's profile, kept strictly per session."""
    profile = st.session_state.get("user_profile", {})
    if profile and profile.get("username"):
        u = profile.get("username")
        try:
            users = _load_users().get("users", {})
            if u in users:
                name_in_file = users[u].get("name")
                if name_in_file and name_in_file != profile.get("name"):
                    profile["name"] = name_in_file
                    st.session_state.user_profile = profile
        except Exception:
            pass
    return profile


def logout():
    """Log out the current user, delete the browser session cookie, and wipe session state."""
    st.session_state.authenticated = False
    st.session_state.user_profile = {}
    st.session_state.logged_out = True
    if "mobile_menu_open" in st.session_state:
        st.session_state.mobile_menu_open = False
    _delete_browser_cookie()
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


def _do_login(username: str, password: str) -> bool:
    """Validate credentials, set persistent browser cookie, and authenticate session."""
    data = _load_users()
    users = data.get("users", {})
    user = users.get(username)
    if user and _verify_password(password, user.get("password", "")):
        profile = {
            "username": username,
            "name": user.get("name") or username,
            "email": user.get("email", ""),
            "role": user.get("role", "reader"),
            "joined": user.get("joined", ""),
        }
        st.session_state.authenticated = True
        st.session_state.user_profile = profile
        st.session_state.logged_out = False
        _set_browser_cookie(username)
        try:
            st.query_params.clear()
        except Exception:
            pass
        return True
    return False


def get_user_now() -> datetime:
    """
    Return timezone-aware current datetime based on the client browser context,
    defaulting gracefully to Indian Standard Time (Asia/Kolkata, UTC+5:30).
    Works reliably on Streamlit Cloud (where the server host runs in UTC) and local environments.
    """
    # 1. Try browser timezone from st.context
    try:
        tz_name = getattr(st.context, "timezone", None)
        if tz_name:
            import zoneinfo
            return datetime.now(zoneinfo.ZoneInfo(tz_name))
    except Exception:
        pass

    # 2. Try browser timezone offset (in minutes from UTC)
    try:
        tz_offset = getattr(st.context, "timezone_offset", None)
        if tz_offset is not None:
            from datetime import timezone, timedelta
            return datetime.now(timezone(timedelta(minutes=-tz_offset)))
    except Exception:
        pass

    # 3. Default to Indian Standard Time (IST, UTC+5:30)
    try:
        import zoneinfo
        return datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))
    except Exception:
        from datetime import timezone, timedelta
        return datetime.now(timezone(timedelta(hours=5, minutes=30)))


def get_time_greeting() -> str:
    """Return an elegant, time-of-day greeting adjusted to the user's local timezone."""
    now = get_user_now()
    h = now.hour
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

    # Immediately authenticate in active session
    st.session_state.authenticated = True
    st.session_state.user_profile = profile
    st.session_state.logged_out = False
    _set_browser_cookie(u)
    try:
        st.query_params.clear()
    except Exception:
        pass

    return True, "Account created successfully!", profile


def render_auth_page():
    """Render the full-page login/signup interface."""

    # Auth page styling with responsive layout
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

    /* Mobile Responsive Overrides for Auth Page */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem 0.6rem !important;
        }
        .auth-brand-header {
            margin: 1.2rem auto 0.8rem !important;
        }
        .auth-brand-name {
            font-size: 1.8rem !important;
        }
        .auth-brand-sub {
            font-size: 0.65rem !important;
            letter-spacing: 1.2px !important;
        }
        /* Make columns full width on phone */
        [data-testid="column"]:nth-child(1),
        [data-testid="column"]:nth-child(3) {
            display: none !important;
        }
        [data-testid="column"]:nth-child(2) {
            width: 100% !important;
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }
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

