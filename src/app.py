"""Streamlit application entrypoint for LeafCheck."""

import json
import streamlit as st

from ocr import extract_text
from report import build_report
from judge_gpt import judge_with_gpt

from db import APP_BASE_URL, supabase_client, supabase_user_client

# ---------------------------
# Page config & styles
# ---------------------------
st.set_page_config(
    page_title="LeafCheck Greenwashing Detector",
    page_icon="🌿",
    layout="wide"
)


def _inject_global_styles() -> None:
    """Apply custom styling so the Streamlit UI matches the design system."""

    st.markdown(
        """

        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

        html, body, [data-testid="stAppViewContainer"] *, [data-testid="block-container"] * {
            font-family: 'Manrope', sans-serif !important;
        }

        body {
            background: linear-gradient(160deg, #f2fbf5 0%, #ffffff 55%, #e6f3ea 100%);
        }

        [data-testid="block-container"] {
            padding-top: 0 !important;
            padding-bottom: 4rem !important;
            max-width: 1180px !important;
        }

        .leaf-shell {
            padding: 0 1.5rem;
        }

        .leaf-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            padding: 1.6rem 0 1.2rem;
            border-bottom: 1px solid rgba(176, 190, 197, 0.35);
        }

        .leaf-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: #2f4239;
        }

        .leaf-brand-name {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.01em;
        }

        .leaf-brand-tagline {
            font-size: 0.85rem;
            color: #5a7462;
        }

        .leaf-nav {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1.25rem;
        }

        .leaf-nav a {
            color: #2f4239;
            font-weight: 600;
            font-size: 0.95rem;
            text-decoration: none;
            transition: color 0.2s ease;
        }

        .leaf-nav a:hover {
            color: #1f2a24;
        }

        .leaf-account-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.5rem 0.9rem;
            border-radius: 999px;
            background: rgba(165, 214, 167, 0.25);
            color: #2f4239;
            font-weight: 600;
        }

        .leaf-account-actions button,
        .leaf-account-trigger button {
            background-color: #2f4239 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 999px !important;
            padding: 0.35rem 1.2rem !important;
        }

        .leaf-account-trigger .stPopover > div > button {
            background: rgba(47, 66, 57, 0.08) !important;
            color: #2f4239 !important;
            border-radius: 999px !important;
            border: 1px solid rgba(47, 66, 57, 0.18) !important;
            font-weight: 600 !important;
            padding: 0.45rem 1.25rem !important;
        }

        .leaf-hero {
            margin-top: 2.5rem;
            border-radius: 1.5rem;
            background: linear-gradient(135deg, rgba(165, 214, 167, 0.18), rgba(120, 180, 150, 0.18));
            padding: clamp(2rem, 5vw, 3.75rem);
            text-align: center;
            box-shadow: 0 20px 50px rgba(92, 125, 104, 0.12);
        }

        .leaf-hero h1 {
            font-size: clamp(2.4rem, 5vw, 3.6rem);
            font-weight: 800;
            color: #1f2a24;
            margin-bottom: 1rem;
            line-height: 1.1;
        }

        .leaf-hero p {
            color: #3e5245;
            font-size: clamp(1rem, 2.4vw, 1.2rem);
            max-width: 620px;
            margin: 0 auto;
        }

        .leaf-upload-card {
            margin-top: 2.5rem;
            border-radius: 1rem;
            border: 1px solid rgba(47, 66, 57, 0.08);
            background: #ffffff;
            padding: clamp(2rem, 4vw, 3.5rem);
            text-align: center;
            box-shadow: 0 16px 40px rgba(47, 66, 57, 0.08);
        }

        .leaf-upload-card h3 {
            font-size: clamp(1.2rem, 3vw, 1.5rem);
            font-weight: 700;
            color: #1f2a24;
            margin-bottom: 0.3rem;
        }

        .leaf-upload-card p {
            color: #5a7462;
            font-size: 0.95rem;
        }

        .leaf-feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .leaf-feature-card {
            border-radius: 1rem;
            border: 1px solid rgba(47, 66, 57, 0.12);
            background: rgba(255, 255, 255, 0.92);
            padding: 1.75rem;
            box-shadow: 0 14px 32px rgba(47, 66, 57, 0.08);
            backdrop-filter: blur(6px);
        }

        .leaf-feature-card h3 {
            margin-top: 0.6rem;
            font-size: 1.15rem;
            font-weight: 700;
            color: #1f2a24;
        }

        .leaf-feature-card p {
            color: #4f6657;
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .leaf-results-card {
            margin-top: 2.5rem;
            border-radius: 1rem;
            background: #ffffff;
            border: 1px solid rgba(47, 66, 57, 0.12);
            box-shadow: 0 18px 45px rgba(47, 66, 57, 0.12);
            padding: clamp(1.75rem, 4vw, 2.5rem);
        }

        .leaf-results-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            align-items: stretch;
        }

        .leaf-score-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 1.1rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.95rem;
        }

        .leaf-score-pill.low {
            background: rgba(165, 214, 167, 0.28);
            color: #1f2a24;
        }

        .leaf-score-pill.medium {
            background: rgba(255, 204, 112, 0.28);
            color: #5a3d00;
        }

        .leaf-score-pill.high {
            background: rgba(255, 153, 153, 0.28);
            color: #7d1f1f;
        }

        .leaf-reasons {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            margin-top: 1rem;
        }

        .leaf-reason-item {
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            background: rgba(47, 66, 57, 0.05);
            color: #2f4239;
        }

        .leaf-footer {
            border-top: 1px solid rgba(176, 190, 197, 0.3);
            padding: 2.5rem 0 1rem;
            color: #607480;
            font-size: 0.9rem;
        }

        .leaf-footer a {
            color: inherit;
            text-decoration: none;
        }

        .leaf-footer a:hover {
            color: #2f4239;
        }

        .leaf-button-primary button {
            background-color: #2f4239 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 999px !important;
            padding: 0.65rem 1.6rem !important;
        }

        [data-testid="stFileUploader"] section {
            padding: 0 !important;
        }

        [data-testid="stFileUploader"] div.stFileUploaderDropzone {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }

        @media (max-width: 768px) {
            .leaf-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1.25rem;
            }

            .leaf-nav {
                justify-content: flex-start;
                gap: 0.9rem;
            }

            .leaf-shell {
                padding: 0 1rem;
            }
        }

        </style>

        """,
        unsafe_allow_html=True,
    )


_inject_global_styles()

# ---------------------------
# Auth helpers (place FIRST)
# ---------------------------

def _initialize_auth_state() -> None:
    """Ensure session state keys exist for auth flows."""

    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "Login"


def _render_account_controls(user) -> None:
    """Render login / account controls within the header."""

    sb_public = supabase_client()

    if user:
        email = getattr(user, "email", "Account")
        st.markdown(
            f"<div class='leaf-account-chip'>🌿 {email}</div>",
            unsafe_allow_html=True,
        )
        with st.popover("Account", use_container_width=True):
            st.markdown(f"**{email}**")
            st.caption("Manage your password or sign out.")
            new_pwd = st.text_input("New password", type="password", key="account_new_pwd")
            confirm_pwd = st.text_input("Confirm password", type="password", key="account_confirm_pwd")
            if st.button("Update password", key="account_update_pwd"):
                if not new_pwd or not confirm_pwd:
                    st.error("Please complete both password fields.")
                elif new_pwd != confirm_pwd:
                    st.error("Passwords do not match.")
                else:
                    try:
                        sb_user = supabase_user_client(st.session_state.get("access_token"))
                        sb_user.auth.update_user({"password": new_pwd})
                        st.success("Password updated.")
                    except Exception as exc:
                        st.error(f"Update error: {exc}")

            if st.button("Log out", key="account_logout"):
                try:
                    sb_public.auth.sign_out()
                except Exception:
                    pass
                st.session_state.user = None
                st.session_state.access_token = None
                st.rerun()
        return

    st.markdown("<div class='leaf-account-trigger'>", unsafe_allow_html=True)
    with st.popover("Sign in", use_container_width=True):
        choices = ["Login", "Sign Up", "Forgot password"]
        try:
            current_index = choices.index(st.session_state.get("auth_tab", "Login"))
        except ValueError:
            current_index = 0

        mode = st.radio(
            "Account",
            choices,
            index=current_index,
            key="auth_tab_selector",
            label_visibility="collapsed",
            horizontal=True,
        )
        st.session_state.auth_tab = mode

        if mode == "Login":
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_submit"):
                try:
                    res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.session_state.access_token = (
                        res.session.access_token if res.session and res.session.access_token else None
                    )
                    st.success("Welcome back!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Auth error: {exc}")

        elif mode == "Sign Up":
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Create account", key="signup_submit"):
                try:
                    sb_public.auth.sign_up({"email": email, "password": password})
                    st.success("Check your inbox to confirm your account.")
                except Exception as exc:
                    st.error(f"Sign up error: {exc}")

        else:  # Forgot password
            email = st.text_input("Account email", key="forgot_email")
            st.caption("We’ll send you a secure link to reset your password.")
            if st.button("Send reset email", key="forgot_submit"):
                try:
                    try:
                        sb_public.auth.reset_password_for_email(
                            email,
                            options={"redirect_to": APP_BASE_URL},
                        )
                    except Exception:
                        sb_public.auth.reset_password_email(
                            email,
                            redirect_to=APP_BASE_URL,
                        )
                    st.success("Password reset email sent.")
                except Exception as exc:
                    st.error(f"Reset error: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_header(user) -> None:
    """Render the hero navigation header with logo and auth shortcuts."""

    with st.container():
        st.markdown("<div class='leaf-shell'>", unsafe_allow_html=True)
        st.markdown("<div class='leaf-header'>", unsafe_allow_html=True)

        brand_col, nav_col, account_col = st.columns([1.5, 1.4, 1.1])

        with brand_col:
            st.markdown(
                """
                <div class="leaf-brand">
                    <div style="width:36px; height:36px; color:#5ea476;">
                        <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.8261 17.4264C16.7203 18.1174 20.2244 18.5217 24 18.5217C27.7756 18.5217 31.2797 18.1174 34.1739 17.4264C36.9144 16.7722 39.9967 15.2331 41.3563 14.1648L24.8486 40.6391C24.4571 41.267 23.5429 41.267 23.1514 40.6391L6.64374 14.1648C8.00331 15.2331 11.0856 16.7722 13.8261 17.4264Z" fill="currentColor"></path>
                            <path clip-rule="evenodd" d="M39.998 12.236C39.9944 12.2537 39.9875 12.2845 39.9748 12.3294C39.9436 12.4399 39.8949 12.5741 39.8346 12.7175C39.8168 12.7597 39.7989 12.8007 39.7813 12.8398C38.5103 13.7113 35.9788 14.9393 33.7095 15.4811C30.9875 16.131 27.6413 16.5217 24 16.5217C20.3587 16.5217 17.0125 16.131 14.2905 15.4811C12.0012 14.9346 9.44505 13.6897 8.18538 12.8168C8.17384 12.7925 8.16216 12.767 8.15052 12.7408C8.09919 12.6249 8.05721 12.5114 8.02977 12.411C8.00356 12.3152 8.00039 12.2667 8.00004 12.2612C8.00004 12.261 8 12.2607 8.00004 12.2612C8.00004 12.2359 8.0104 11.9233 8.68485 11.3686C9.34546 10.8254 10.4222 10.2469 11.9291 9.72276C14.9242 8.68098 19.1919 8 24 8C28.8081 8 33.0758 8.68098 36.0709 9.72276C37.5778 10.2469 38.6545 10.8254 39.3151 11.3686C39.9006 11.8501 39.9857 12.1489 39.998 12.236ZM4.95178 15.2312L21.4543 41.6973C22.6288 43.5809 25.3712 43.5809 26.5457 41.6973L43.0534 15.223C43.0709 15.1948 43.0878 15.1662 43.104 15.1371L41.3563 14.1648C43.104 15.1371 43.1038 15.1374 43.104 15.1371L43.1051 15.135L43.1065 15.1325L43.1101 15.1261L43.1199 15.1082C43.1276 15.094 43.1377 15.0754 43.1497 15.0527C43.1738 15.0075 43.2062 14.9455 43.244 14.8701C43.319 14.7208 43.4196 14.511 43.5217 14.2683C43.6901 13.8679 44 13.0689 44 12.2609C44 10.5573 43.003 9.22254 41.8558 8.2791C40.6947 7.32427 39.1354 6.55361 37.385 5.94477C33.8654 4.72057 29.133 4 24 4C18.867 4 14.1346 4.72057 10.615 5.94478C8.86463 6.55361 7.30529 7.32428 6.14419 8.27911C4.99695 9.22255 3.99999 10.5573 3.99999 12.2609C3.99999 13.1275 4.29264 13.9078 4.49321 14.3607C4.60375 14.6102 4.71348 14.8196 4.79687 14.9689C4.83898 15.0444 4.87547 15.1065 4.9035 15.1529C4.91754 15.1762 4.92954 15.1957 4.93916 15.2111L4.94662 15.223L4.95178 15.2312ZM35.9868 18.996L24 38.22L12.0131 18.996C12.4661 19.1391 12.9179 19.2658 13.3617 19.3718C16.4281 20.1039 20.0901 20.5217 24 20.5217C27.9099 20.5217 31.5719 20.1039 34.6383 19.3718C35.082 19.2658 35.5339 19.1391 35.9868 18.996Z" fill="currentColor" fill-rule="evenodd"></path>
                        </svg>
                    </div>
                    <div>
                        <div class="leaf-brand-name">LeafCheck</div>
                        <div class="leaf-brand-tagline">AI Greenwashing Detector</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with nav_col:
            st.markdown(
                """
                <nav class="leaf-nav">
                    <a href="#analysis">Dashboard</a>
                    <a href="#history">History</a>
                    <a href="#about">About</a>
                </nav>
                """,
                unsafe_allow_html=True,
            )

        with account_col:
            _render_account_controls(user)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_hero_section() -> None:
    """Display the marketing hero copy."""

    with st.container():
        st.markdown(
            """
            <div class="leaf-shell">
                <section class="leaf-hero" id="about">
                    <h1>Instant GPT reviews for environmental claims.</h1>
                    <p>While we rework our in-house algorithm, LeafCheck now leans entirely on GPT to surface risky marketing promises, highlight missing evidence, and suggest what to fix.</p>
                </section>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_features_section() -> None:
    """Show the three feature highlights from the design."""

    with st.container():
        st.markdown(
            """
            <div class="leaf-shell" id="history">
                <div class="leaf-feature-grid">
                    <div class="leaf-feature-card">
                        <span class='material-symbols-outlined' style='color:#5ea476; font-size:2rem;'>bolt</span>
                        <h3>GPT-first risk scoring</h3>
                        <p>Every review now comes straight from our GPT auditor, ensuring consistent, conservative EU-style guidance while we iterate on the rule engine.</p>
                    </div>
                    <div class="leaf-feature-card">
                        <span class='material-symbols-outlined' style='color:#5ea476; font-size:2rem;'>search_insights</span>
                        <h3>Clear rationale</h3>
                        <p>See the exact rationale behind the score with concise bullets you can hand to copywriters, compliance leads, or clients.</p>
                    </div>
                    <div class="leaf-feature-card">
                        <span class='material-symbols-outlined' style='color:#5ea476; font-size:2rem;'>description</span>
                        <h3>Downloadable evidence</h3>
                        <p>Export a polished PDF summarizing the GPT judgement, OCR text, and next steps so you can share the findings instantly.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_footer() -> None:
    """Render footer links and social icons."""

    with st.container():
        st.markdown(
            """
            <footer class="leaf-footer">
                <div style="display:flex; flex-wrap:wrap; gap:1.25rem; justify-content:space-between; align-items:center;">
                    <span>© 2024 LeafCheck. All rights reserved.</span>
                    <div style="display:flex; gap:1.5rem;">
                        <a class="leaf-nav-link" style="margin-right:0; color:#B0BEC5;" href="#">Terms of Service</a>
                        <a class="leaf-nav-link" style="margin-right:0; color:#B0BEC5;" href="#">Privacy Policy</a>
                    </div>
                    <div style="display:flex; gap:1rem; color:#B0BEC5;">
                        <span>Twitter</span>
                        <span>LinkedIn</span>
                        <span>Facebook</span>
                    </div>
                </div>
            </footer>
            """,
            unsafe_allow_html=True,
        )


def render_upload_section():
    """Render the drag-and-drop inspired upload card and return the uploaded file."""

    with st.container():
        st.markdown("<div class='leaf-shell' id='analysis'>", unsafe_allow_html=True)
        st.markdown('<div class="leaf-upload-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:flex; flex-direction:column; align-items:center; gap:0.75rem;">
                <div style="font-size:3rem; color:#5ea476;">
                    <span class='material-symbols-outlined' style='font-size:3.2rem;'>cloud_upload</span>
                </div>
                <h3>Drop your creative and let GPT inspect it.</h3>
                <p>JPG or PNG works great. We’ll extract the copy, run the GPT judge, and package the findings for you.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        st.markdown('</div></div>', unsafe_allow_html=True)
    return uploaded

def current_user():
    return st.session_state.get("user")


def ensure_user_profile_initialized():
    """Create or refresh the app_users profile row for the logged-in user."""

    user = current_user()
    if not user or st.session_state.get("_profile_ready"):
        return

    access_token = st.session_state.get("access_token")
    sb = supabase_user_client(access_token)
    payload = {
        "user_id": user.id,
        "email": getattr(user, "email", None),
    }

    try:
        sb.table("app_users").upsert(payload, on_conflict="user_id").execute()
        st.session_state["_profile_ready"] = True
    except Exception as exc:
        message = str(exc).lower()
        if "duplicate" in message or "conflict" in message:
            st.session_state["_profile_ready"] = True
        else:
            # Leave the flag unset so we can retry later, but avoid surfacing noisy errors.
            st.session_state["_profile_ready"] = False

# ---------------------------
# DB logging helpers
# ---------------------------
def save_analysis(user_id, image_name, ocr_text, leaf_score, leaf_level, triggers,
                  gpt_score=None, gpt_reason=None, combined_score=None):
    """
    Inserts an analysis row and returns the created analysis_id (uuid) if available.
    Uses user-authenticated client so RLS sees auth.uid().
    """
    access_token = st.session_state.get("access_token")
    sb = supabase_user_client(access_token)

    # Ensure triggers is JSON-serializable dict
    if not isinstance(triggers, dict):
        try:
            triggers = json.loads(triggers) if isinstance(triggers, str) else {}
        except Exception:
            triggers = {}

    row = {
        "user_id": user_id,
        "image_name": image_name,
        "ocr_text": ocr_text,
        "leaf_score": int(leaf_score) if leaf_score is not None else None,
        "leaf_level": leaf_level,
        "triggers": triggers,
        "gpt_score": int(gpt_score) if gpt_score is not None else None,
        "gpt_reason": gpt_reason,
        "combined_score": int(combined_score) if combined_score is not None else None,
    }
    def _attempt_insert():
        res = sb.table("analyses").insert(row).execute()
        inserted = (res.data or [])
        return inserted[0]["id"] if inserted and "id" in inserted[0] else None

    try:
        return _attempt_insert()
    except Exception as exc:
        message = str(exc)
        if "403" in message:
            # First-time users may not yet have their profile row for RLS policies. Try to create it.
            ensure_user_profile_initialized()
            try:
                return _attempt_insert()
            except Exception as retry_exc:
                message = str(retry_exc)
        st.warning(
            "Could not save this analysis to Supabase yet. We saved the results locally; "
            "please try again later."
        )
        st.caption(f"Supabase error detail: {message}")
        return None

def feedback_widget(analysis_id: str):
    st.markdown("**Was this score accurate?**")
    label = st.radio(
        "Pick one",
        ["correct", "too_high", "too_low", "not_applicable"],
        horizontal=True,
        key=f"fb_choice_{analysis_id}"
    )
    comment = st.text_area("Optional comment", key=f"fb_comment_{analysis_id}")
    if st.button("Submit feedback", key=f"fb_submit_{analysis_id}"):
        access_token = st.session_state.get("access_token")
        sb = supabase_user_client(access_token)
        try:
            sb.table("feedback").insert({
                "analysis_id": analysis_id,
                "user_id": current_user().id,
                "label": label,
                "comment": comment
            }).execute()
            st.success("Thanks for the feedback!")
        except Exception as e:
            st.error(f"Feedback error: {e}")


def render_analysis_results(
    *,
    gpt_score: int,
    gpt_level: str,
    gpt_reasons: list[str],
    gpt_error: bool,
    gpt_error_message: str,
    analysis_id: str | None,
    image_bytes: bytes,
    extracted_text: str,
    results: dict,
):
    """Render the GPT-only analysis card and supporting utilities."""

    lvl = (gpt_level or "").lower()
    level_class = lvl if lvl in {"low", "medium", "high"} else "low"
    friendly_level = gpt_level or "Low"

    level_messages = {
        "high": "High risk — absolute or sweeping environmental claims need evidence.",
        "medium": "Medium risk — tighten the scope and add substantiation before publishing.",
        "low": "Low risk — claims look specific and factual, keep references handy.",
    }

    summary_message = level_messages.get(level_class, "Risk level unavailable.")
    reasons = [str(r) for r in (gpt_reasons or []) if str(r).strip()]
    error_message = (gpt_error_message or "").strip()

    with st.container():
        st.markdown("<div class='leaf-shell'>", unsafe_allow_html=True)
        st.markdown("<section class='leaf-results-card' id='results'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom:0.75rem;'>GPT Risk Review</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='leaf-score-pill {level_class}'>Risk level: {friendly_level.title()}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='margin-top:0.8rem; font-size:1.05rem; color:#2f4239;'>Score: <strong>{gpt_score}</strong> / 100</p>",
            unsafe_allow_html=True,
        )

        if gpt_error:
            fallback_message = error_message or (reasons[0] if reasons else "GPT review fell back to a safe default.")
            st.warning(fallback_message)

        st.markdown(f"<p style='color:#3e5245; margin-top:0.4rem;'>{summary_message}</p>", unsafe_allow_html=True)

        if reasons:
            st.markdown("<div class='leaf-reasons'>", unsafe_allow_html=True)
            for reason in reasons:
                st.markdown(
                    """
                    <div class='leaf-reason-item'>
                        <span class='material-symbols-outlined' style='font-size:1.2rem; color:#5ea476;'>task_alt</span>
                        <span>{reason}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("GPT did not provide additional rationale for this review.")

        st.markdown("<hr style='margin:2rem 0; border:none; border-top:1px solid rgba(47,66,57,0.12);' />", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:0.5rem;'>Extracted Text</h3>", unsafe_allow_html=True)
        if extracted_text:
            st.code(extracted_text, language="text")
        else:
            st.warning("No text detected in the creative.")

        st.markdown("<h3 style='margin-top:1.8rem;'>Download report</h3>", unsafe_allow_html=True)
        with st.spinner("Preparing PDF..."):
            pdf_bytes, fname = build_report(
                image_bytes=image_bytes,
                extracted_text=extracted_text,
                results=results,
            )

        st.download_button(
            "⬇️ Download GPT report",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            type="primary",
            help="Save the GPT score, reasons, and OCR transcript.",
        )

        if analysis_id:
            st.markdown("<h3 style='margin-top:1.8rem;'>Feedback</h3>", unsafe_allow_html=True)
            feedback_widget(analysis_id)

        st.markdown("</section></div>", unsafe_allow_html=True)

    if level_class == "high":
        st.error(summary_message)
    elif level_class == "medium":
        st.warning(summary_message)
    elif level_class == "low":
        st.success(summary_message)
    else:
        st.info(summary_message)

# ---------------------------
# UI start
# ---------------------------
_initialize_auth_state()

render_header(st.session_state.user)
render_hero_section()
uploaded = render_upload_section()
render_features_section()

user = current_user()
if user:
    ensure_user_profile_initialized()
else:
    st.session_state.auth_tab = "Login"

if uploaded is None:
    render_footer()
    st.stop()

# Read image bytes and keep filename
image_bytes = uploaded.read()
image_name = uploaded.name

with st.spinner("Running OCR..."):
    extracted_text = extract_text(image_bytes)

with st.spinner("Reviewing with GPT..."):
    gpt_out = judge_with_gpt(extracted_text) or {}
    if not isinstance(gpt_out, dict):
        gpt_out = {
            "risk_score": 0,
            "level": "Low",
            "reasons": ["LLM judge error."],
            "_error": True,
            "_error_message": "GPT review failed due to an unexpected response.",
        }

gpt_score = int(gpt_out.get("risk_score", 0) or 0)
gpt_level = str(gpt_out.get("level", "Low") or "Low")
gpt_reasons = gpt_out.get("reasons", []) or []
gpt_error = bool(gpt_out.get("_error"))
gpt_error_message = str(gpt_out.get("_error_message") or "").strip()

if isinstance(gpt_reasons, list):
    reasons_for_storage = [str(r) for r in gpt_reasons if str(r).strip()]
elif isinstance(gpt_reasons, str):
    reasons_for_storage = [gpt_reasons]
else:
    reasons_for_storage = [json.dumps(gpt_reasons)]

report_results = {
    "score": gpt_score,
    "level": gpt_level.title(),
    "ai_label": "GPT Review",
    "ai_confidence": 100.0 if not gpt_error else 0.0,
    "triggers": {},
    "recommendations": reasons_for_storage,
}

if user:
    gpt_reason = "\n".join(reasons_for_storage)
    analysis_id = save_analysis(
        user_id=user.id,
        image_name=image_name,
        ocr_text=extracted_text,
        leaf_score=gpt_score,
        leaf_level=gpt_level,
        triggers={},
        gpt_score=gpt_score,
        gpt_reason=gpt_reason,
        combined_score=gpt_score,
    )
else:
    analysis_id = None

render_analysis_results(
    gpt_score=gpt_score,
    gpt_level=gpt_level,
    gpt_reasons=reasons_for_storage,
    gpt_error=gpt_error,
    gpt_error_message=gpt_error_message,
    analysis_id=analysis_id,
    image_bytes=image_bytes,
    extracted_text=extracted_text,
    results=report_results,
)

render_footer()
