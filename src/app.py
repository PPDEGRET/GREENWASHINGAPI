# src/app.py
import os
import json
import streamlit as st

from ocr import extract_text
from analyzer import analyze_text, blend_with_llm, DEFAULT_LLM_WEIGHT
from recommender import recommend
from report import build_report
from judge_gpt import judge_with_gpt

from db import supabase_client, supabase_user_client

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="LeafCheck Greenwashing Detector",
    page_icon="🌿",
    layout="centered"
)

# ---------------------------
# Auth helpers (place FIRST)
# ---------------------------
from db import supabase_client, supabase_user_client, APP_BASE_URL


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

def auth_block():
    """
    Sidebar auth with Login / Sign up / Forgot Password (logged-out)
    and Change Password (logged-in).
    Stores:
      - st.session_state.user
      - st.session_state.access_token
    """
    sb_public = supabase_client()  # anon client for auth endpoints

    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    with st.sidebar:
        st.header("Account")

        # --------------------------
        # Logged OUT views
        # --------------------------
        if st.session_state.user is None:
            mode = st.radio(
                "Account",
                ["Login", "Sign up", "Forgot password"],
                horizontal=True
            )

            if mode in ("Login", "Sign up"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")

                if mode == "Sign up":
                    if st.button("Create account"):
                        try:
                            sb_public.auth.sign_up({"email": email, "password": password})
                            st.success("Check your email to confirm your account.")
                        except Exception as e:
                            st.error(f"Sign up error: {e}")
                else:
                    if st.button("Login"):
                        try:
                            res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
                            # Save user + token for RLS
                            st.session_state.user = res.user
                            st.session_state.access_token = (
                                res.session.access_token if res.session and res.session.access_token else None
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Login error: {e}")

            elif mode == "Forgot password":
                fp_email = st.text_input("Your account email")
                st.caption("We’ll email you a secure link to reset your password.")
                if st.button("Send reset email"):
                    try:
                        # Supabase Python clients may expose either of these; we try both for compatibility.
                        try:
                            # Newer name
                            sb_public.auth.reset_password_for_email(
                                fp_email,
                                options={"redirect_to": APP_BASE_URL}
                            )
                        except Exception:
                            # Fallback name
                            sb_public.auth.reset_password_email(
                                fp_email,
                                redirect_to=APP_BASE_URL
                            )
                        st.success("Password reset email sent. Check your inbox and follow the link.")
                        st.info("After you’re back in the app, use 'Login' and then 'Change password' if needed.")
                    except Exception as e:
                        st.error(f"Reset error: {e}")

        # --------------------------
        # Logged IN views
        # --------------------------
        else:
            st.write(f"Signed in as: {st.session_state.user.email}")

            # Change password UI
            with st.expander("Change password"):
                new_pwd = st.text_input("New password", type="password", key="np1")
                new_pwd2 = st.text_input("Confirm new password", type="password", key="np2")
                if st.button("Update password"):
                    if not new_pwd:
                        st.error("Please enter a new password.")
                    elif new_pwd != new_pwd2:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            # Use user-authenticated client (carries JWT) so update works securely
                            sb_user = supabase_user_client(st.session_state.get("access_token"))
                            sb_user.auth.update_user({"password": new_pwd})
                            st.success("Password updated.")
                        except Exception as e:
                            st.error(f"Update error: {e}")

            # Logout button
            if st.button("Log out"):
                try:
                    sb_public.auth.sign_out()
                except Exception:
                    pass
                st.session_state.user = None
                st.session_state.access_token = None
                st.rerun()

def current_user():
    return st.session_state.get("user")

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
    try:
        res = sb.table("analyses").insert(row).execute()
        inserted = (res.data or [])
        return inserted[0]["id"] if inserted and "id" in inserted[0] else None
    except Exception as e:
        st.warning(f"Could not save analysis (db error): {e}")
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

# ---------------------------
# UI start
# ---------------------------
st.title("🌿 LeafCheck — Ad Screenshot Analyzer")
st.write("Upload an ad screenshot (PNG or JPG) and let AI flag potential greenwashing claims.")

# (Optional) quick debug badges
st.sidebar.caption(f"SB URL OK: {bool(os.getenv('SUPABASE_URL'))}")
st.sidebar.caption(f"Auth token present: {bool(st.session_state.get('access_token'))}")

# Auth UI (sidebar)
auth_block()
user = current_user()
if user is None:
    st.info("Please log in to run analyses.")
    st.stop()

# Premium gating
is_premium = user_is_premium(user.id)
if not is_premium:
    st.warning("Free plan: OCR + rule-based score. Upgrade to premium to use GPT Judge.")
allow_gpt = is_premium

# Controls
colA, colB = st.columns([1, 1])
with colA:
    use_gpt = st.toggle(
        "Use GPT Judge (experimental)",
        value=False if not allow_gpt else False,
        help="Adds a second opinion using a GPT model.",
        disabled=not allow_gpt
    )
with colB:
    combine_scores = st.toggle(
        "Show Combined Score",
        value=True,
        help="Display a weighted average of LeafCheck + GPT."
    )

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
if not uploaded:
    st.info("Upload an ad image to begin.")
    st.stop()

# Read image bytes and keep filename
image_bytes = uploaded.read()
image_name = uploaded.name

# OCR
with st.spinner("Running OCR..."):
    extracted_text = extract_text(image_bytes)

st.write("### 📝 Extracted Text")
if extracted_text:
    st.code(extracted_text, language="text")
else:
    st.warning("No text detected in the image.")

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

# Optional GPT judge
gpt_out = {}
if use_gpt:
    with st.spinner("Getting GPT second opinion..."):
        gpt_out = judge_with_gpt(extracted_text) or {}
        if not isinstance(gpt_out, dict):
            gpt_out = {"risk_score": 0, "level": "Low", "reasons": ["LLM judge error."], "_error": True}

# Compute combined if needed
final = None
final_lvl = None
if use_gpt and combine_scores:
    combo = blend_with_llm(results, gpt_out, llm_weight=DEFAULT_LLM_WEIGHT)
    final = combo["score"]
    final_lvl = combo["level"]
else:
    combo = None

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

analysis_id = save_analysis(
    user_id=user.id,
    image_name=image_name,
    ocr_text=extracted_text,
    leaf_score=score,
    leaf_level=level,
    triggers=triggers,
    gpt_score=gpt_score,
    gpt_reason=gpt_reason,
    combined_score=combo["score"] if combo else None
)

# ---------------------------
# Scores section
# ---------------------------
st.subheader("⚖️ Greenwashing Risk")

if use_gpt and combine_scores:
    lc_col, gpt_col, final_col = st.columns(3)
elif use_gpt:
    lc_col, gpt_col = st.columns(2)
    final_col = None
else:
    (lc_col,) = st.columns(1)
    gpt_col = final_col = None

with lc_col:
    st.metric("LeafCheck Score", f"{score}", help=score_tooltip)
    st.caption(f"Level: **{level}** — HF label: {ai_label} ({ai_conf:.1f}% confidence)")

if use_gpt and gpt_col is not None:
    gj_score = int(gpt_out.get("risk_score", 0) or 0)
    gj_level = str(gpt_out.get("level", "Low"))
    with gpt_col:
        st.metric("GPT Judge", f"{gj_score}")
        st.caption(f"Level: **{gj_level}**")

if use_gpt and combine_scores and final_col is not None:
    with final_col:
        st.metric("Final (Combined)", f"{final}")
        weights = combo.get("weights", {}) if combo else {}
        rule_w = weights.get("rule")
        llm_w = weights.get("llm")
        if rule_w is not None and llm_w is not None:
            st.caption(
                f"Level: **{final_lvl}** — blend LeafCheck {rule_w:.0%} / GPT {llm_w:.0%}"
            )
        else:
            st.caption(f"Level: **{final_lvl}**")

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

st.download_button(
    "⬇️ Download PDF Report",
    data=pdf_bytes,
    file_name=fname,
    mime="application/pdf",
    type="primary",
    help="Saves the image, risk summary, triggers, recommendations, and OCR text."
)

# Final message
final_level_for_message = final_lvl if (use_gpt and combine_scores and combo) else level
lvl = (final_level_for_message or "").lower()
if lvl == "high":
    st.error("High risk — strong or absolute environmental claims without clear scope/evidence.")
elif lvl == "medium":
    st.warning("Medium risk — general or partially supported claims. Add specificity/evidence.")
elif lvl == "low":
    st.success("Low risk — claims appear specific and factual.")
else:
    st.info("Risk level unavailable.")
