from __future__ import annotations
from typing import Dict, List

# Prioritized rules → we’ll return up to 3 tips
def recommend(triggers: Dict[str, List[str]], extracted_text: str = "") -> List[str]:
    t = {k: set(v or []) for k, v in (triggers or {}).items()}
    tips: List[str] = []

    # 1) Absolute / superlative claims
    if t.get("superlatives"):
        tips.append(
            "Avoid **absolute environmental claims** (e.g., “carbon neutral”, “100% sustainable”) unless the scope is narrow, current, and backed by **independent verification**."
        )

    # 2) Offsets / compensation
    if t.get("offsets"):
        tips.append(
            "If mentioning **offsets**, state **what is offset**, **which standard** (e.g., Verra/Gold Standard), **who buys it**, and avoid implying overall climate neutrality."
        )

    # 3) Future targets / timelines
    if t.get("future_claims"):
        tips.append(
            "For **future targets** (e.g., “10% by 2030”), provide the **baseline**, **scope** (well-to-wake vs tank-to-wake), **assumptions**, and **verification plan**."
        )

    # 4) Vague framing / minimization
    if t.get("vague_frames"):
        tips.append(
            "Avoid **vague framing** (e.g., “only”, “just”) without context; add **absolute figures** and cite reputable sources."
        )

    # 5) Methodology / evidence missing (works even if you add this category later)
    needs_method = t.get("methodologyNeeds") or t.get("methodology_needs") or []
    if needs_method and not t.get("certifications"):
        tips.append(
            "Provide **methodology & boundaries** (functional unit, system boundaries, time frame), and link to a **public methodology page**."
        )

    # 6) Certifications not present
    if not t.get("certifications"):
        tips.append(
            "Reference **recognized standards/certifications** where applicable (e.g., EU Ecolabel, ISO 14001) and link to supporting evidence."
        )

    # Fallback (if nothing triggered)
    if not tips:
        tips.append(
            "Ensure claims are **specific, verifiable, and up-to-date**; include links to supporting evidence."
        )

    # Return up to 3 concise, non-duplicated tips
    out: List[str] = []
    for tip in tips:
        if tip not in out:
            out.append(tip)
        if len(out) == 3:
            break
    return out
