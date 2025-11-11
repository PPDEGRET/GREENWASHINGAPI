# AGENTS.md — LeafCheck Project Guidelines

Project: LeafCheck — AI Greenwashing Detector / Ad Screenshot Analyzer  
Purpose: Guide AI agents and contributors to make consistent, safe, and well-structured changes.

-------------------------------------------------------------------------------

## Architecture Overview

Folder structure:

/src  
 ├── app.py          → Streamlit UI entrypoint  
 ├── ocr.py          → OCR text extraction (EasyOCR / RapidOCR)  
 ├── judge_gpt.py    → GPT-based risk scoring  
 ├── report.py       → PDF export (ReportLab)  
 ├── db.py           → Supabase integration  
 └── config.py       → Environment variable loader  

/web                 → Static marketing site (index.html, styles.css, main.js, assets/)  
/web-legacy          → Archived Next.js frontend (do not modify)  
/.devcontainer       → Codespaces config + secret mapping  

Environment variables (never hard-code):
OPENAI_API_KEY  
SUPABASE_URL  
SUPABASE_ANON_KEY  
SUPABASE_SERVICE_ROLE  
APP_BASE_URL  (default http://localhost:8501)

-------------------------------------------------------------------------------

## Do

### UX and Style
- Keep the Stitch / Material-3 aesthetic used in /web and src/app.py
- Use Manrope font (Google Fonts)
- Use design tokens (no raw hex codes):

  --bg: #f7fbf8;  
  --text: #1f2a24;  
  --muted: #4f6657;  
  --brand: #5ea476;  
  --brand-strong: #2f4239;  
  --card: #ffffff;  
  --border: rgba(47,66,57,0.12);

- Ensure responsive layouts (360px → 1440px+)
- Prefer small components and small diffs

### Backend Logic
- Reuse existing modules (ocr.py, judge_gpt.py, report.py, db.py)
- Load .env via python-dotenv locally; inject with --env-file in Docker or Codespaces remoteEnv
- Risk score: integer 0–100, level ∈ {Low, Medium, High}
- "Triggers": short, user-friendly reasons
- "Ameliorations": actionable compliance improvements

### General
- Keep changes atomic
- Write clear, explicit commit messages
- Always test locally before pushing

-------------------------------------------------------------------------------

## Don't

- Do not hard-code secrets, URLs, or colors
- Do not add heavy dependencies without approval (no Tailwind, no React rebuilds)
- Do not edit /web-legacy unless explicitly requested
- Do not fetch data directly inside UI components (use helpers or clients)

-------------------------------------------------------------------------------

## File-Scoped Commands

Prefer per-file checks; avoid full repo builds unless asked.

### Python
python -m black path/to/file.py  
python -m ruff check --fix path/to/file.py  
pytest -q tests/test_some_module.py

### Web (Static)
npx prettier --write web/index.html web/styles.css web/main.js

### Run Apps
python -m streamlit run src/app.py --server.address=0.0.0.0 --server.port=8501  
cd web && python -m http.server 5500

### Docker Example
docker run --rm -p 8501:8501 --env-file .env ^
  -v "%CD%\src:/app/src" leafcheck

-------------------------------------------------------------------------------

## Safety and Permissions

Allowed without confirmation:
- Read and list files
- Lint, format, and test single files
- Small edits and refactors

Ask before doing:
- Installing or removing packages
- Deleting or renaming directories
- Large refactors or repo-wide rewrites
- Running production builds or deployments

-------------------------------------------------------------------------------

## Project Pointers

UI: src/app.py → see _inject_global_styles() and render_* functions  
Logic: judge_gpt.py, ocr.py, report.py  
Supabase: db.py (use user client for RLS inserts)  
Static site: /web (pure HTML/CSS/JS, no build tools)

Good patterns:
- Use CSS variables in /web/styles.css
- Follow component structure in render_analysis_results

Avoid:
- Material icons (task_alt) in Streamlit markdown
- Mixing legacy Next.js code into /web

-------------------------------------------------------------------------------

## PR Checklist

- Descriptive title (feat(scope): summary)
- Lint, format, and tests all green
- Diff small and scoped
- No secrets or debug logs
- Manual checks:
  - Streamlit runs on port 8501
  - Static site runs on port 5500
  - "Open App" link points to correct URL
  - PDF export works

-------------------------------------------------------------------------------

## When Stuck

If uncertain:
1. Ask a clarifying question
2. Propose a short plan before executing
3. Open a draft PR with notes if unsure

-------------------------------------------------------------------------------

## Design System Quick Reference

Typography: Manrope  
Colors: use tokens above  
Buttons: pill shape, brand green background, white text  
Cards: rounded (16–24px), soft shadows, subtle borders  
Dividers: use --border  
Focus state: visible and accessible outlines

-------------------------------------------------------------------------------

## Multi-Agent Pointers

For tools like Claude, Cursor, Builder, etc., create pointer files at the repo root:

# CLAUDE.md / CURSOR.md / BUILDER.md
Strictly follow the rules in ./AGENTS.md

-------------------------------------------------------------------------------

Keep this file concise and evolving.  
Add new "Do" and "Don't" rules when patterns repeat or quality drifts.
