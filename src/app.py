"""Streamlit application entrypoint for LeafCheck."""

import json
import streamlit as st

from ocr import extract_text
from analyzer import analyze_text
from recommender import recommend
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

        [data-testid="block-container"] {
            padding-top: 0 !important;
            padding-bottom: 4rem !important;
        }

        .leaf-primary {
            color: #37474F;
        }

        .leaf-muted {
            color: #B0BEC5;
        }

        .leaf-pill {
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
        }

        .leaf-upload-card {
            border: 2px dashed rgba(176, 190, 197, 0.5);
            border-radius: 0.75rem;
            padding: 3.5rem 1.5rem;
            background: #FFFFFF;
            text-align: center;
        }

        .leaf-upload-card h3 {
            font-size: 1.125rem;
            font-weight: 700;
            color: #37474F;
            margin-bottom: 0.25rem;
        }

        .leaf-upload-card p {
            font-size: 0.9rem;
            color: #B0BEC5;
        }

        .leaf-section {
            padding: 0 1.5rem;
        }

        .leaf-hero {
            text-align: center;
            padding: 4rem 1rem 3rem;
        }

        .leaf-hero h1 {
            font-size: clamp(2.5rem, 5vw, 3.5rem);
            font-weight: 800;
            color: #37474F;
            margin-bottom: 1rem;
        }

        .leaf-hero p {
            color: #37474F;
            font-size: 1.1rem;
            margin: 0 auto;
            max-width: 640px;
        }

        .leaf-feature-card {
            border: 1px solid rgba(176, 190, 197, 0.3);
            border-radius: 0.75rem;
            background: #FFFFFF;
            padding: 1.75rem;
            height: 100%;
        }

        .leaf-feature-card h3 {
            margin-top: 0.5rem;
            font-size: 1.125rem;
            font-weight: 700;
            color: #37474F;
        }

        .leaf-feature-card p {
            color: #607480;
            font-size: 0.95rem;
        }

        .leaf-footer {
            border-top: 1px solid rgba(176, 190, 197, 0.3);
            padding: 2.5rem 1.5rem 1rem;
            color: #B0BEC5;
            font-size: 0.9rem;
        }

        .leaf-button-primary button {
            background-color: #A5D6A7 !important;
            color: #37474F !important;
            font-weight: 700 !important;
            border-radius: 0.5rem !important;
        }

        .leaf-button-outline button {
            background-color: rgba(165, 214, 167, 0.2) !important;
            color: #37474F !important;
            font-weight: 700 !important;
            border-radius: 0.5rem !important;
        }

        .leaf-nav-link {
            color: #37474F;
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
            margin-right: 1.5rem;
        }

        .leaf-nav-link:hover {
            color: #2b353a;
        }

        [data-testid="stFileUploader"] section {
            padding: 0 !important;
        }

        [data-testid="stFileUploader"] div.stFileUploaderDropzone {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }

        .leaf-analysis-card {
            background: #FFFFFF;
            border-radius: 0.75rem;
            border: 1px solid rgba(176, 190, 197, 0.3);
            padding: 2rem;
        }

        .leaf-section-title {
            color: #37474F;
            font-weight: 700;
            font-size: 1.35rem;
            margin-bottom: 1rem;
        }

        .leaf-pill-muted {
            background: rgba(165, 214, 167, 0.2);
            color: #37474F;
            border-radius: 9999px;
            padding: 0.35rem 0.9rem;
            font-weight: 600;
            font-size: 0.85rem;
        }

        .leaf-auth-card {
            background: #F7FBF7;
            border: 1px solid rgba(165, 214, 167, 0.4);
            border-radius: 0.75rem;
            padding: 2rem;
            margin: 1rem 0 2.5rem;
        }

        .leaf-auth-card h3 {
            margin-bottom: 0.75rem;
            color: #37474F;
            font-weight: 700;
        }

        .leaf-auth-card .stTextInput>div>div>input,
        .leaf-auth-card .stTextArea>div>div>textarea,
        .leaf-auth-card .stTextInput>div>label,
        .leaf-auth-card label {
            font-family: 'Manrope', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


_inject_global_styles()

# ---------------------------
# Auth helpers (place FIRST)
# ---------------------------


def _format_breakdown_tooltip(breakdown: dict) -> str | None:
    """Create a readable tooltip describing how the LeafCheck score was built."""

    if not isinstance(breakdown, dict):
        return None

    risk_terms = breakdown.get("risk_terms") or {}
    evidence_terms = breakdown.get("evidence_terms") or {}
    r_raw = breakdown.get("R_raw")
    e_total = breakdown.get("E")
    r_damped = breakdown.get("R_damped")

    risk_labels = {
        "carbon_neutral": "Carbon-neutral claims",
        "offsets": "Offsets volume",
        "lifecycle_offset": "Lifecycle offset claims",
        "absolutes": "Absolute statements",
        "superlatives": "Superlatives & hype",
        "vague": "Vague language",
        "packaging_only": "Packaging-only claim",
        "sector_interaction": "Sector risk interaction",
        "offset_reliance": "Offset reliance",
        "llm_greenwash": "LLM greenwashing signal",
    }

    evidence_labels = {
        "third_party": "Third-party assurance",
        "lca_epd": "LCA / EPD evidence",
        "standards": "Standards cited",
        "scope": "Scopes disclosed",
        "specificity": "Specificity (%, baseline, target)",
        "citation": "External citations",
    }

    def _format_section(title: str, entries: dict, labels: dict) -> list[str]:
        lines: list[str] = []
        if not entries:
            return lines
        filtered = {k: float(v) for k, v in entries.items() if abs(float(v)) > 1e-3}
        if not filtered:
            return lines
        lines.append(title)
        for key, value in sorted(filtered.items(), key=lambda item: -abs(item[1])):
            label = labels.get(key, key.replace("_", " ").title())
            lines.append(f"• {label}: {value:+.2f}")
        return lines

    tooltip_lines: list[str] = []
    tooltip_lines.extend(_format_section("Risk factors:", risk_terms, risk_labels))
    tooltip_lines.extend(_format_section("Evidence dampers:", evidence_terms, evidence_labels))

    aggregate_bits = []
    if isinstance(r_raw, (int, float)):
        aggregate_bits.append(f"R_raw={float(r_raw):.2f}")
    if isinstance(e_total, (int, float)):
        aggregate_bits.append(f"Evidence sum={float(e_total):.2f}")
    if isinstance(r_damped, (int, float)):
        aggregate_bits.append(f"R_damped={float(r_damped):.2f}")
    if aggregate_bits:
        tooltip_lines.append("Aggregates: " + ", ".join(aggregate_bits))

    return "\n".join(tooltip_lines) if tooltip_lines else None

def _initialize_auth_state() -> None:
    """Ensure session state keys exist for auth flows."""

    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "auth_panel_mode" not in st.session_state:
        st.session_state.auth_panel_mode = "Login"
    if "show_auth_panel" not in st.session_state:
        st.session_state.show_auth_panel = True


def render_header(user) -> None:
    """Render the hero navigation header with logo and auth shortcuts."""

    with st.container():
        st.markdown(
            "<div style='padding: 1.5rem 0 1.25rem; border-bottom: 1px solid rgba(176,190,197,0.3);'>",
            unsafe_allow_html=True,
        )
        left, center, right = st.columns([1.4, 1.6, 1.4])

        with left:
            st.markdown(
                """
                <div style="display:flex; align-items:center; gap:0.75rem; color:#37474F;">
                    <div style="width:36px; height:36px; color:#A5D6A7;">
                        <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.8261 17.4264C16.7203 18.1174 20.2244 18.5217 24 18.5217C27.7756 18.5217 31.2797 18.1174 34.1739 17.4264C36.9144 16.7722 39.9967 15.2331 41.3563 14.1648L24.8486 40.6391C24.4571 41.267 23.5429 41.267 23.1514 40.6391L6.64374 14.1648C8.00331 15.2331 11.0856 16.7722 13.8261 17.4264Z" fill="currentColor"></path>
                            <path clip-rule="evenodd" d="M39.998 12.236C39.9944 12.2537 39.9875 12.2845 39.9748 12.3294C39.9436 12.4399 39.8949 12.5741 39.8346 12.7175C39.8168 12.7597 39.7989 12.8007 39.7813 12.8398C38.5103 13.7113 35.9788 14.9393 33.7095 15.4811C30.9875 16.131 27.6413 16.5217 24 16.5217C20.3587 16.5217 17.0125 16.131 14.2905 15.4811C12.0012 14.9346 9.44505 13.6897 8.18538 12.8168C8.17384 12.7925 8.16216 12.767 8.15052 12.7408C8.09919 12.6249 8.05721 12.5114 8.02977 12.411C8.00356 12.3152 8.00039 12.2667 8.00004 12.2612C8.00004 12.261 8 12.2607 8.00004 12.2612C8.00004 12.2359 8.0104 11.9233 8.68485 11.3686C9.34546 10.8254 10.4222 10.2469 11.9291 9.72276C14.9242 8.68098 19.1919 8 24 8C28.8081 8 33.0758 8.68098 36.0709 9.72276C37.5778 10.2469 38.6545 10.8254 39.3151 11.3686C39.9006 11.8501 39.9857 12.1489 39.998 12.236ZM4.95178 15.2312L21.4543 41.6973C22.6288 43.5809 25.3712 43.5809 26.5457 41.6973L43.0534 15.223C43.0709 15.1948 43.0878 15.1662 43.104 15.1371L41.3563 14.1648C43.104 15.1371 43.1038 15.1374 43.104 15.1371L43.1051 15.135L43.1065 15.1325L43.1101 15.1261L43.1199 15.1082C43.1276 15.094 43.1377 15.0754 43.1497 15.0527C43.1738 15.0075 43.2062 14.9455 43.244 14.8701C43.319 14.7208 43.4196 14.511 43.5217 14.2683C43.6901 13.8679 44 13.0689 44 12.2609C44 10.5573 43.003 9.22254 41.8558 8.2791C40.6947 7.32427 39.1354 6.55361 37.385 5.94477C33.8654 4.72057 29.133 4 24 4C18.867 4 14.1346 4.72057 10.615 5.94478C8.86463 6.55361 7.30529 7.32428 6.14419 8.27911C4.99695 9.22255 3.99999 10.5573 3.99999 12.2609C3.99999 13.1275 4.29264 13.9078 4.49321 14.3607C4.60375 14.6102 4.71348 14.8196 4.79687 14.9689C4.83898 15.0444 4.87547 15.1065 4.9035 15.1529C4.91754 15.1762 4.92954 15.1957 4.93916 15.2111L4.94662 15.223L4.95178 15.2312ZM35.9868 18.996L24 38.22L12.0131 18.996C12.4661 19.1391 12.9179 19.2658 13.3617 19.3718C16.4281 20.1039 20.0901 20.5217 24 20.5217C27.9099 20.5217 31.5719 20.1039 34.6383 19.3718C35.082 19.2658 35.5339 19.1391 35.9868 18.996Z" fill="currentColor" fill-rule="evenodd"></path>
                        </svg>
                    </div>
                    <div>
                        <div style="font-size:1.25rem; font-weight:800;">LeafCheck</div>
                        <div style="font-size:0.85rem; color:#607480;">AI Greenwashing Detector</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with center:
            st.markdown(
                """
                <div style="display:flex; justify-content:center; align-items:center; gap:1.5rem; margin-top:0.25rem;">
                    <a class="leaf-nav-link" href="#analysis">Dashboard</a>
                    <a class="leaf-nav-link" href="#history">History</a>
                    <a class="leaf-nav-link" href="#about">About</a>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            if user:
                st.markdown(
                    f"""
                    <div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.25rem; color:#37474F;">
                        <span style="font-size:0.9rem;">Signed in as</span>
                        <strong style="font-size:1rem;">{getattr(user, 'email', 'Account')}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                logout_container = st.container()
                with logout_container:
                    st.markdown('<div class="leaf-button-outline">', unsafe_allow_html=True)
                    if st.button("Log out", use_container_width=True, key="header_logout"):
                        sb_public = supabase_client()
                        try:
                            sb_public.auth.sign_out()
                        except Exception:
                            pass
                        st.session_state.user = None
                        st.session_state.access_token = None
                        st.session_state.show_auth_panel = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="leaf-button-outline">', unsafe_allow_html=True)
                    if st.button("Login", use_container_width=True, key="header_login"):
                        st.session_state.auth_panel_mode = "Login"
                        st.session_state.show_auth_panel = True
                    st.markdown('</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="leaf-button-primary">', unsafe_allow_html=True)
                    if st.button("Sign Up", use_container_width=True, key="header_signup"):
                        st.session_state.auth_panel_mode = "Sign up"
                        st.session_state.show_auth_panel = True
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


def auth_section() -> None:
    """Render authentication controls styled like the reference design."""

    sb_public = supabase_client()

    user = st.session_state.user

    with st.container():
        st.markdown('<div class="leaf-auth-card" id="about">', unsafe_allow_html=True)

        if user is None:
            st.markdown("<h3>Access your account</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='color:#607480; margin-bottom:1rem;'>Log in or create an account to unlock premium GPT judging and save analyses to your history.</p>",
                unsafe_allow_html=True,
            )

            mode = st.radio(
                "Account",
                ["Login", "Sign up", "Forgot password"],
                horizontal=True,
                key="auth_mode_radio",
                index=["Login", "Sign up", "Forgot password"].index(st.session_state.auth_panel_mode),
            )
            st.session_state.auth_panel_mode = mode

            if mode in ("Login", "Sign up"):
                email = st.text_input("Email", key=f"{mode.lower()}_email")
                password = st.text_input("Password", type="password", key=f"{mode.lower()}_password")

                submit_label = "Create account" if mode == "Sign up" else "Login"
                with st.container():
                    st.markdown('<div class="leaf-button-primary">', unsafe_allow_html=True)
                    if st.button(submit_label, use_container_width=True, key=f"{mode.lower()}_submit"):
                        try:
                            if mode == "Sign up":
                                sb_public.auth.sign_up({"email": email, "password": password})
                                st.success("Check your email to confirm your account.")
                            else:
                                res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
                                st.session_state.user = res.user
                                st.session_state.access_token = (
                                    res.session.access_token if res.session and res.session.access_token else None
                                )
                                st.session_state.show_auth_panel = False
                                st.rerun()
                        except Exception as exc:
                            st.error(f"Auth error: {exc}")
                    st.markdown('</div>', unsafe_allow_html=True)

            else:
                fp_email = st.text_input("Your account email", key="forgot_email")
                st.caption("We’ll send you a secure link to reset your password.")
                with st.container():
                    st.markdown('<div class="leaf-button-primary">', unsafe_allow_html=True)
                    if st.button("Send reset email", use_container_width=True, key="forgot_submit"):
                        try:
                            try:
                                sb_public.auth.reset_password_for_email(
                                    fp_email,
                                    options={"redirect_to": APP_BASE_URL},
                                )
                            except Exception:
                                sb_public.auth.reset_password_email(
                                    fp_email,
                                    redirect_to=APP_BASE_URL,
                                )
                            st.success("Password reset email sent. Check your inbox.")
                            st.info("After resetting, return here and use Login to access premium features.")
                        except Exception as exc:
                            st.error(f"Reset error: {exc}")
                    st.markdown('</div>', unsafe_allow_html=True)

        else:
            email = getattr(user, "email", "Account")
            st.markdown(f"<h3>Welcome back, {email}</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='color:#607480; margin-bottom:1.2rem;'>Manage your account and update your password from here.</p>",
                unsafe_allow_html=True,
            )

            with st.expander("Change password", expanded=False):
                new_pwd = st.text_input("New password", type="password", key="np1")
                new_pwd2 = st.text_input("Confirm new password", type="password", key="np2")
                with st.container():
                    st.markdown('<div class="leaf-button-primary">', unsafe_allow_html=True)
                    if st.button("Update password", use_container_width=True, key="update_password"):
                        if not new_pwd:
                            st.error("Please enter a new password.")
                        elif new_pwd != new_pwd2:
                            st.error("Passwords do not match.")
                        else:
                            try:
                                sb_user = supabase_user_client(st.session_state.get("access_token"))
                                sb_user.auth.update_user({"password": new_pwd})
                                st.success("Password updated.")
                            except Exception as exc:
                                st.error(f"Update error: {exc}")
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def render_hero_section() -> None:
    """Display the marketing hero copy."""

    with st.container():
        st.markdown(
            """
            <section class="leaf-hero">
                <h1>Upload an ad — get a greenwashing risk analysis.</h1>
                <p>Our AI analyzes your marketing materials to identify potential greenwashing risks and provides a detailed report.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )


def render_features_section() -> None:
    """Show the three feature highlights from the design."""

    with st.container():
        st.markdown('<div class="leaf-section" id="history">', unsafe_allow_html=True)
        st.markdown('<div style="padding:2.5rem 0;">', unsafe_allow_html=True)
        cols = st.columns(3)
        features = [
            (
                "assessment",
                "Understand Your Score",
                "Get a clear and concise risk score for your ad, with a detailed breakdown of the factors that influenced the score.",
            ),
            (
                "auto_awesome",
                "AI-Powered Insights",
                "Our advanced AI analyzes your ad's text and imagery to provide you with actionable insights and recommendations.",
            ),
            (
                "workspace_premium",
                "Go Premium",
                "Unlock advanced features like detailed reports, historical analysis, and competitive benchmarking.",
            ),
        ]

        for col, (icon, title, copy) in zip(cols, features):
            with col:
                st.markdown(
                    f"""
                    <div class='leaf-feature-card'>
                        <div style='color:#A5D6A7; font-size:2rem;'>
                            <span class='material-symbols-outlined'>{icon}</span>
                        </div>
                        <h3>{title}</h3>
                        <p>{copy}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('</div></div>', unsafe_allow_html=True)


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
        st.markdown('<div class="leaf-section" id="analysis">', unsafe_allow_html=True)
        st.markdown('<div class="leaf-upload-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:flex; flex-direction:column; align-items:center; gap:0.75rem;">
                <div style="font-size:3rem; color:#A5D6A7;">
                    <span class='material-symbols-outlined' style='font-size:3.2rem;'>upload_file</span>
                </div>
                <h3>Drag & drop a file here or browse your files.</h3>
                <p>Our AI will analyze your ad for greenwashing.</p>
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

def user_is_premium(user_id: str) -> bool:
    access_token = st.session_state.get("access_token")
    sb = supabase_user_client(access_token)
    try:
        data = sb.table("app_users").select("is_premium").eq("user_id", user_id).execute()
        rows = data.data or []
        return bool(rows and rows[0].get("is_premium"))
    except Exception:
        return False

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
    score,
    level,
    ai_label,
    ai_conf,
    score_tooltip,
    breakdown,
    triggers,
    tips,
    use_gpt,
    gpt_out,
    analysis_id,
    image_bytes,
    extracted_text,
    results,
):
    """Render the styled analysis results card."""

    with st.container():
        st.markdown('<div class="leaf-section">', unsafe_allow_html=True)
        st.markdown('<div class="leaf-analysis-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="leaf-section-title">Greenwashing Risk</h2>', unsafe_allow_html=True)

        if use_gpt:
            lc_col, gpt_col = st.columns(2)
        else:
            (lc_col,) = st.columns(1)
            gpt_col = None

        with lc_col:
            st.metric("LeafCheck Score", f"{score}", help=score_tooltip)
            st.caption(f"Level: **{level}** — HF label: {ai_label} ({ai_conf:.1f}% confidence)")

        if use_gpt and gpt_col is not None:
            gj_score = int(gpt_out.get("risk_score", 0) or 0)
            gj_level = str(gpt_out.get("level", "Low"))
            with gpt_col:
                st.metric("GPT Judge", f"{gj_score}")
                st.caption(f"Level: **{gj_level}**")

        if breakdown:
            st.markdown(
                "<h3 class='leaf-section-title' style='font-size:1.1rem;'>Score Breakdown</h3>",
                unsafe_allow_html=True,
            )
            nice = {
                "strong_claims": "Strong claims",
                "supporting_claims": "Supporting language",
                "sector_bonus": "Sector context bonus",
                "evidence_adjustment": "Evidence adjustments",
                "model_nudge": "Model nudges",
            }
            for key, label in nice.items():
                if key in breakdown and breakdown[key]:
                    st.caption(f"- {label}: {breakdown[key]:+.1f} pts")

        st.markdown(
            "<h3 class='leaf-section-title' style='font-size:1.1rem;'>Triggered Categories</h3>",
            unsafe_allow_html=True,
        )
        shown_any = False
        for k in sorted(triggers.keys()):
            vals = sorted(set(v for v in triggers.get(k, []) if v))
            if vals:
                shown_any = True
                st.write(f"- **{k}**: {', '.join(vals)}")
        if not shown_any:
            st.caption("No rule-based triggers detected.")

        if tips:
            st.markdown(
                "<h3 class='leaf-section-title' style='font-size:1.1rem;'>Recommendations</h3>",
                unsafe_allow_html=True,
            )
            for t in tips:
                st.write(f"- {t}")

        if use_gpt and isinstance(gpt_out, dict):
            reasons = gpt_out.get("reasons", [])
            if reasons:
                st.markdown(
                    "<h3 class='leaf-section-title' style='font-size:1.1rem;'>GPT Judge — Rationale</h3>",
                    unsafe_allow_html=True,
                )
                for r in reasons:
                    st.write(f"- {r}")

        if analysis_id:
            st.markdown(
                "<h3 class='leaf-section-title' style='font-size:1.1rem;'>Feedback</h3>",
                unsafe_allow_html=True,
            )
            feedback_widget(analysis_id)

        st.markdown(
            "<h3 class='leaf-section-title' style='font-size:1.1rem;'>Export Report</h3>",
            unsafe_allow_html=True,
        )
        with st.spinner("Preparing PDF..."):
            pdf_bytes, fname = build_report(
                image_bytes=image_bytes,
                extracted_text=extracted_text,
                results=results,
            )

        st.download_button(
            "⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            type="primary",
            help="Saves the image, risk summary, triggers, recommendations, and OCR text.",
        )

        final_level_for_message = gpt_out.get("level") if use_gpt else level
        lvl = (final_level_for_message or "").lower()
        if lvl == "high":
            st.error("High risk — strong or absolute environmental claims without clear scope/evidence.")
        elif lvl == "medium":
            st.warning("Medium risk — general or partially supported claims. Add specificity/evidence.")
        elif lvl == "low":
            st.success("Low risk — claims appear specific and factual.")
        else:
            st.info("Risk level unavailable.")

        st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------------------
# UI start
# ---------------------------
_initialize_auth_state()

render_header(st.session_state.user)
render_hero_section()
auth_section()
uploaded = render_upload_section()
render_features_section()

user = current_user()
if user:
    ensure_user_profile_initialized()
    is_premium = user_is_premium(user.id)
else:
    is_premium = False

allow_gpt = bool(user) and is_premium

if uploaded is None:
    render_footer()
    st.stop()

# Read image bytes and keep filename
image_bytes = uploaded.read()
image_name = uploaded.name

with st.container():
    st.markdown('<div class="leaf-section">', unsafe_allow_html=True)
    st.markdown('<div class="leaf-analysis-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="leaf-section-title">Analysis Controls</h2>', unsafe_allow_html=True)

    if not allow_gpt:
        if user:
            st.markdown(
                "<div class='leaf-pill-muted'>Free plan: OCR + rule-based score. Upgrade to premium to use the GPT Judge.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='leaf-pill-muted'>Log in with a premium account to enable the GPT Judge.</div>",
                unsafe_allow_html=True,
            )

    use_gpt = st.toggle(
        "Use GPT Judge (experimental)",
        value=False,
        help="Adds a second opinion using a GPT model.",
        disabled=not allow_gpt,
    )

if user and not is_premium:
    st.warning("Free plan: OCR + rule-based score. Upgrade to premium to use GPT Judge.")

allow_gpt = bool(user) and is_premium
if not allow_gpt:
    if user:
        st.sidebar.info("Upgrade to a premium plan to enable the GPT Judge.")
    else:
        st.sidebar.info("Log in with a premium account to enable the GPT Judge.")

# Controls
use_gpt = st.toggle(
    "Use GPT Judge (experimental)",
    value=False,
    help="Adds a second opinion using a GPT model.",
    disabled=not allow_gpt
)

    st.markdown('</div></div>', unsafe_allow_html=True)

# OCR
with st.spinner("Running OCR..."):
    extracted_text = extract_text(image_bytes)

with st.container():
    st.markdown('<div class="leaf-section">', unsafe_allow_html=True)
    st.markdown('<div class="leaf-analysis-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="leaf-section-title">Extracted Text</h2>', unsafe_allow_html=True)
    if extracted_text:
        st.code(extracted_text, language="text")
    else:
        st.warning("No text detected in the image.")
    st.markdown('</div></div>', unsafe_allow_html=True)

# Analyze (LeafCheck Rules + HF nudge)
with st.spinner("Analyzing (LeafCheck)..."):
    results = analyze_text(extracted_text)

score = int(results.get("score", 0))
level = str(results.get("level", "Low"))
ai_label = str(results.get("ai_label", "—"))
try:
    ai_conf = float(results.get("ai_confidence", 0.0) or 0.0)
except Exception:
    ai_conf = 0.0
triggers = results.get("triggers", {}) or {}
breakdown = results.get("breakdown", {}) or {}
score_tooltip = _format_breakdown_tooltip(breakdown)
tips = recommend(triggers, extracted_text)

# Optional GPT judge
gpt_out = {}
if use_gpt:
    with st.spinner("Getting GPT second opinion..."):
        gpt_out = judge_with_gpt(extracted_text) or {}
        if not isinstance(gpt_out, dict):
            gpt_out = {"risk_score": 0, "level": "Low", "reasons": ["LLM judge error."], "_error": True}

# ---------------------------
# SAVE to DB (right after results are ready)
# ---------------------------
gpt_score = int(gpt_out.get("risk_score", 0) or 0) if use_gpt else None
gpt_reason = None
if use_gpt:
    reasons = gpt_out.get("reasons", [])
    if isinstance(reasons, list):
        gpt_reason = "\n".join([str(r) for r in reasons])
    elif isinstance(reasons, str):
        gpt_reason = reasons
    else:
        gpt_reason = json.dumps(reasons)

if user:
    analysis_id = save_analysis(
        user_id=user.id,
        image_name=image_name,
        ocr_text=extracted_text,
        leaf_score=score,
        leaf_level=level,
        triggers=triggers,
        gpt_score=gpt_score,
        gpt_reason=gpt_reason,
        combined_score=None,
        combined_score=None
    )
else:
    analysis_id = None

with st.container():
    st.markdown('<div class="leaf-section">', unsafe_allow_html=True)
    st.markdown('<div class="leaf-analysis-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="leaf-section-title">Greenwashing Risk</h2>', unsafe_allow_html=True)

    if use_gpt:
        lc_col, gpt_col = st.columns(2)
    else:
        (lc_col,) = st.columns(1)
        gpt_col = None

    with lc_col:
        st.metric("LeafCheck Score", f"{score}", help=score_tooltip)
        st.caption(f"Level: **{level}** — HF label: {ai_label} ({ai_conf:.1f}% confidence)")

    if use_gpt and gpt_col is not None:
        gj_score = int(gpt_out.get("risk_score", 0) or 0)
        gj_level = str(gpt_out.get("level", "Low"))
        with gpt_col:
            st.metric("GPT Judge", f"{gj_score}")
            st.caption(f"Level: **{gj_level}**")

    if breakdown:
        st.markdown("<h3 class='leaf-section-title' style='font-size:1.1rem;'>Score Breakdown</h3>", unsafe_allow_html=True)
        nice = {
            "strong_claims": "Strong claims",
            "supporting_claims": "Supporting language",
            "sector_bonus": "Sector context bonus",
            "evidence_adjustment": "Evidence adjustments",
            "model_nudge": "Model nudges",
        }
        for key, label in nice.items():
            if key in breakdown and breakdown[key]:
                st.caption(f"- {label}: {breakdown[key]:+.1f} pts")

    st.markdown("<h3 class='leaf-section-title' style='font-size:1.1rem;'>Triggered Categories</h3>", unsafe_allow_html=True)
    shown_any = False
    for k in sorted(triggers.keys()):
        vals = sorted(set(v for v in triggers.get(k, []) if v))
        if vals:
            shown_any = True
            st.write(f"- **{k}**: {', '.join(vals)}")
    if not shown_any:
        st.caption("No rule-based triggers detected.")

    tips = recommend(triggers, extracted_text)
    if tips:
        st.markdown("<h3 class='leaf-section-title' style='font-size:1.1rem;'>Recommendations</h3>", unsafe_allow_html=True)
        for t in tips:
            st.write(f"- {t}")

    if use_gpt and isinstance(gpt_out, dict):
        reasons = gpt_out.get("reasons", [])
        if reasons:
            st.markdown("<h3 class='leaf-section-title' style='font-size:1.1rem;'>GPT Judge — Rationale</h3>", unsafe_allow_html=True)
            for r in reasons:
                st.write(f"- {r}")

    if analysis_id:
        st.markdown("<h3 class='leaf-section-title' style='font-size:1.1rem;'>Feedback</h3>", unsafe_allow_html=True)
        feedback_widget(analysis_id)

    st.markdown("<h3 class='leaf-section-title' style='font-size:1.1rem;'>Export Report</h3>", unsafe_allow_html=True)
    with st.spinner("Preparing PDF..."):
        pdf_bytes, fname = build_report(
            image_bytes=image_bytes,
            extracted_text=extracted_text,
            results=results,
        )

    st.download_button(
        "⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name=fname,
        mime="application/pdf",
        type="primary",
        help="Saves the image, risk summary, triggers, recommendations, and OCR text.",
if use_gpt:
    lc_col, gpt_col = st.columns(2)
else:
    (lc_col,) = st.columns(1)
    gpt_col = None

with lc_col:
    st.metric("LeafCheck Score", f"{score}", help=score_tooltip)
    st.caption(f"Level: **{level}** — HF label: {ai_label} ({ai_conf:.1f}% confidence)")

if use_gpt and gpt_col is not None:
    gj_score = int(gpt_out.get("risk_score", 0) or 0)
    gj_level = str(gpt_out.get("level", "Low"))
    with gpt_col:
        st.metric("GPT Judge", f"{gj_score}")
        st.caption(f"Level: **{gj_level}**")

# Breakdown of rule-based contributions

if breakdown:
    st.write("### 📊 LeafCheck Score Breakdown")
    nice = {
        "strong_claims": "Strong claims",
        "supporting_claims": "Supporting language",
        "sector_bonus": "Sector context bonus",
        "evidence_adjustment": "Evidence adjustments",
        "model_nudge": "Model nudges",
    }
    for key, label in nice.items():
        if key in breakdown and breakdown[key]:
            st.caption(f"- {label}: {breakdown[key]:+.1f} pts")

# Triggers
st.write("### 🚨 Triggered Categories")
shown_any = False
for k in sorted(triggers.keys()):
    vals = sorted(set(v for v in triggers.get(k, []) if v))
    if vals:
        shown_any = True
        st.write(f"- **{k}**: {', '.join(vals)}")
if not shown_any:
    st.caption("No rule-based triggers detected.")

# Recommendations
tips = recommend(triggers, extracted_text)
if tips:
    st.write("### 💡 Recommendations")
    for t in tips:
        st.write(f"- {t}")

# GPT rationale (if any)
if use_gpt and isinstance(gpt_out, dict):
    reasons = gpt_out.get("reasons", [])
    if reasons:
        st.write("### 🧠 GPT Judge — Rationale")
        for r in reasons:
            st.write(f"- {r}")

# Feedback widget (requires analysis_id)
if analysis_id:
    st.write("---")
    st.write("### 🗳️ Feedback")
    feedback_widget(analysis_id)

# PDF Report
st.write("---")
st.write("### 📄 Export Report")
with st.spinner("Preparing PDF..."):
    pdf_bytes, fname = build_report(
        image_bytes=image_bytes,
        extracted_text=extracted_text,
        results=results
    )

    final_level_for_message = gpt_out.get("level") if use_gpt else level
    lvl = (final_level_for_message or "").lower()
    if lvl == "high":
        st.error("High risk — strong or absolute environmental claims without clear scope/evidence.")
    elif lvl == "medium":
        st.warning("Medium risk — general or partially supported claims. Add specificity/evidence.")
    elif lvl == "low":
        st.success("Low risk — claims appear specific and factual.")
    else:
        st.info("Risk level unavailable.")

    st.markdown('</div></div>', unsafe_allow_html=True)

render_footer()
# Final message
final_level_for_message = gpt_out.get("level") if use_gpt else level
lvl = (final_level_for_message or "").lower()
if lvl == "high":
    st.error("High risk — strong or absolute environmental claims without clear scope/evidence.")
elif lvl == "medium":
    st.warning("Medium risk — general or partially supported claims. Add specificity/evidence.")
elif lvl == "low":
    st.success("Low risk — claims appear specific and factual.")
else:
    st.info("Risk level unavailable.")
