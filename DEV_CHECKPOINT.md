🧭 Dev Checkpoint Doc — LeafCheck (AI Greenwashing Detector)

Date: October 2025
Maintainer: Henri Brown

🌿 Project Name

LeafCheck — AI Greenwashing Detector / Ad Screenshot Analyzer

Purpose:
Upload an ad (PNG/JPG), extract its text (OCR), analyze potential greenwashing risk (rule-based + AI), and export a PDF report summarizing risk levels, triggers, and recommendations.

⚙️ Current Environment & Stack
🧰 Runtime / Container

Running fully online via GitHub Codespaces

Python 3.11 (devcontainer image: mcr.microsoft.com/devcontainers/python:3.11)

Streamlit app running on port 8501

Persistent development container (devcontainer.json at repo root) with automatic pip install and secrets injection for both container and remote VS Code sessions

Supabase backend for Auth, DB, and storage

🧩 Key Python Libraries

streamlit, rapidocr-onnxruntime, transformers, torch (CPU),
reportlab, pillow, opencv-python-headless,
supabase, openai, httpx==0.27.2, numpy

🗂️ File / Folder Structure
/src/
   app.py              ← main Streamlit app (UI + workflow)
   analyzer.py         ← recalibrated rule/ML scoring pipeline
   ocr.py              ← RapidOCR text extraction with preprocessing
   recommender.py      ← generates improvement tips
   report.py           ← PDF export (ReportLab)
   judge_gpt.py        ← GPT-based second opinion
   db.py               ← Supabase client helpers (env-aware)
   config.py           ← centralized settings + env validation
   risk_rules.py       ← rule definitions for analyzer
   utils.py            ← misc helpers
/dockerfile
/requirements.txt
/devcontainer.json
/DEV_CHECKPOINT.md     ← this document

🌍 Environment Variables (.env or Codespaces Secrets)
OPENAI_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE= (optional, only required for admin flows)
APP_BASE_URL=http://localhost:8501 (defaulted in code if unset)

✅ Working Features
1. Core App Flow

Image upload (PNG/JPG)

OCR text extraction via RapidOCR with CLAHE/denoise preprocessing fallback

Hybrid analysis:

- Rule-based triggers (keywords: “carbon neutral”, “offsets”, “recycled plastic”, etc.)
- Evidence dampening logic (third-party assurance, specificity, scopes)
- Zero-shot transformer nudge (facebook/bart-large-mnli) to adjust risk trend
- Recalibrated score blending raw risk, damped risk, and mitigation factors for clearer Low/Medium/High levels

GPT Judge (optional, premium only):

- Uses OpenAI API for second opinion when enabled
- Independent score + rationale display (no more combined toggle)

PDF Report export:

Image, extracted text, scores, triggers, recommendations

Streamlit UI updates:

- GPT toggle disabled unless a premium user is logged in
- Sidebar guidance for anonymous/free users
- Score breakdown tooltips surface risk/evidence contributions

2. Auth + Database Integration (Supabase)

Sidebar login/signup/logout + forgot password + change password

Premium gating: GPT judge only available for app_users.is_premium = true

Feedback loop: logged-in users can submit rating/comment linked to saved analysis rows

Analyses logged to Supabase via user-authenticated client; automatic profile upsert for first-time users

Environment-aware clients via config.py ensure secrets are loaded consistently across runtime contexts

3. Dev Environment

Codespaces: auto-install via devcontainer.json postCreate command

Ports forwarded automatically (8501)

Manual launch via:

python -m streamlit run src/app.py --server.address=0.0.0.0 --server.port=8501

⚠️ Known Issues / Roadblocks

RapidOCR model (~120 MB) loads on first use; warm-up spinner may take a few seconds

Feedback + analysis logging still depend on Supabase RLS; transient failures are surfaced as Streamlit warnings but results remain local only

GPT Judge requires OPENAI_API_KEY; UI displays fallback messaging when missing or when user lacks premium access

🚀 Next Steps
🔹 Short-Term

🧠 Polish RapidOCR confidence filtering (store spans + confidences for auditing)

🧩 Finalize feedback analytics view inside the app or a separate admin dashboard

🎨 Continue UI polish: responsive layout for score cards + breakdown, lighten copy

🔹 Mid-Term

🧾 Persist all analyses with timestamps & sector metadata for historical trends

📊 Build Supabase dashboard or Streamlit admin page for feedback and trigger insights

💬 Add fact-checking step (cross-check claims against eco-label datasets)

🧱 Explore caching for OCR/analysis results to reduce latency per request

🔹 Long-Term

📦 Deploy public version (Streamlit Community Cloud / Hugging Face Spaces / Cloud Run)

👥 Add subscription / Stripe integration for premium management

🧮 Train custom greenwashing classifier (fine-tune ClimateBERT/DistilRoBERTa)

🪄 Offer AI-assisted claim rewriting (“How to make this statement compliant”)

💾 Last Known Good State

LeafCheck runs in Codespaces via:

python -m streamlit run src/app.py --server.address=0.0.0.0 --server.port=8501

Anonymous users: OCR + LeafCheck scoring + PDF export (no Supabase writes)

Premium logged-in users: GPT Judge toggle, saved analyses, feedback submission

Supabase keys validated by config.py; environment mismatches raise explicit errors

✅ End of Dev Checkpoint — LeafCheck (AI Greenwashing Tool)
