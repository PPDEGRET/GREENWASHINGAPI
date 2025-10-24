# src/analyzer.py
from __future__ import annotations
from typing import Dict, List
import re
import streamlit as st
from transformers import pipeline

# -------------------------------
# Model (used as a nudge, not a judge)
# -------------------------------
@st.cache_resource(show_spinner=False)
def _clf():
    """
    Load the zero-shot classifier once per process.
    We keep it as a semantic nudge; rules carry the main load.
    """
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1
    )

# -------------------------------
# Phrase patterns & detectors
# -------------------------------
# Core claim patterns
RX = {
    "carbon_neutral": re.compile(r"\bcarbon[-\s]?neutral\b", re.I),
    "offsets": re.compile(r"\b(offset(?:ting)?|carbon\s*credits?|compensat(?:e|ion)|insetting)\b", re.I),
    "lifecycle_offset": re.compile(r"(life[-\s]?cycle).+?(offset|credits?)", re.I),
    # Vague terms
    "vague_terms": re.compile(r"\b(sustainable|green|eco\b|planet[-\s]?friendly|environmentally\s*friendly)\b", re.I),
    # Absolutes
    "absolutes": re.compile(r"\b(100%|always|never|zero\s*impact|no\s*emissions|completely|entirely)\b", re.I),
    # Comparatives / superlatives frequently used for hype
    "comparatives": re.compile(
        r"\b(cleanest|greenest|most\s+sustainable|most\s+efficient|lowest\s*emissions|best\s+for\s+the\s+planet|ultimate)\b",
        re.I
    ),
    # Packaging claims (supportive, weaker alone)
    "packaging": re.compile(r"\b(recyclable|recycled\s*plastic|biodegradable|compostable|sustainable\s*packaging)\b", re.I),
}

# Sector context (higher scrutiny)
SECTOR_RX = re.compile(
    r"\b(airline|airlines|aviation|airways|flight|ryanair|oil|petrol|gas|fossil|energy|utility|utilities|"
    r"fashion|apparel|fast\s*fashion|shipping|cruise|automotive|car\s*maker)\b",
    re.I
)

# Evidence / substantiation cues
EVIDENCE_RX = {
    "pas2060": re.compile(r"\bPAS\s*2060\b", re.I),
    "iso14021": re.compile(r"\bISO\s*14021\b", re.I),
    "iso14067": re.compile(r"\bISO\s*14067\b", re.I),
    "scope": re.compile(r"\bscope\s*(1|2|3)\b", re.I),
    "third_party": re.compile(r"\b(third[-\s]?party|independent)\s*(verified|assured|verification)\b", re.I),
    "epd_lca": re.compile(r"\b(EPD|environmental\s+product\s+declaration|LCA|life\s+cycle\s+assessment)\b", re.I),
    "link": re.compile(r"https?://\S+", re.I),  # crude URL catch
}

CANDIDATE_LABELS = [
    "greenwashing",
    "vague environmental claim",
    "offsetting claim",
    "packaging claim",
    "specific substantiated claim",
    "no environmental claim",
]

# -------------------------------
# Helpers
# -------------------------------
def _find_triggers(text: str) -> Dict[str, List[str]]:
    t = text or ""
    hits: Dict[str, List[str]] = {}

    # Packaging: list exact hits
    pkg = RX["packaging"].findall(t)
    if pkg:
        hits["Packaging"] = sorted(set([p.lower() for p in pkg]))

    # Comparatives/Superlatives: list exact hits (include carbon neutral in this list if present)
    comps = RX["comparatives"].findall(t)
    # Also surface "carbon neutral" as hype when phrased with "ultimate"/etc
    if RX["carbon_neutral"].search(t):
        comps = list(comps) + ["carbon neutral"]
    if comps:
        hits["Superlatives"] = sorted(set([c.lower() for c in comps]))

    # Vague terms
    vague = RX["vague_terms"].findall(t)
    if vague:
        hits["Vague Claims"] = sorted(set([v.lower() for v in vague]))

    # Absolutes
    abs_hits = RX["absolutes"].findall(t)
    if abs_hits:
        hits["Absolutes"] = sorted(set([a.lower() for a in abs_hits]))

    # Offsets
    if RX["offsets"].search(t):
        hits["Offsets"] = ["offset/credits"]

    # Lifecycle offset mention
    if RX["lifecycle_offset"].search(t):
        hits["Lifecycle Offset"] = ["lifecycle + offset"]

    # Carbon neutral explicit
    if RX["carbon_neutral"].search(t):
        hits["Carbon Neutral"] = ["carbon neutral"]

    # Sector
    if SECTOR_RX.search(t):
        hits["Sector Context"] = ["high-impact sector"]

    return hits

def _label_score(labels: List[str], scores: List[float], name: str) -> float:
    try:
        i = labels.index(name)
        return float(scores[i])
    except ValueError:
        return 0.0

def _evidence_strength(text: str) -> int:
    """
    Return number of distinct evidence types detected (0..7).
    This is a crude proxy; we only use it to gently reduce risk.
    """
    t = text or ""
    kinds = 0
    for rx in EVIDENCE_RX.values():
        if rx.search(t):
            kinds += 1
    return kinds

# -------------------------------
# Main
# -------------------------------
def analyze_text(text: str) -> Dict[str, object]:
    text = (text or "").strip()
    if not text:
        return {
            "score": 0,
            "level": "Low",
            "ai_label": "no environmental claim",
            "ai_confidence": 100.0,
            "triggers": {}
        }

    t_low = text.lower()

    # 1) Rule triggers
    triggers = _find_triggers(t_low)

    # 2) Base scoring from rules (strong, transparent)
    score = 0.0

    # Strong signals
    if "Carbon Neutral" in triggers:
        score += 40
    if "Offsets" in triggers:
        score += 25
    if "Lifecycle Offset" in triggers:
        score += 18

    # Support signals
    if "Absolutes" in triggers:
        score += 14
    if "Vague Claims" in triggers:
        # +10 plus +1 per distinct vague term (max +15)
        score += min(15, 10 + max(0, len(triggers["Vague Claims"]) - 1))
    if "Superlatives" in triggers:
        # comparatives like "cleanest/greenest/most sustainable" are strong
        # baseline +10 plus +3 per distinct item (cap +25)
        score += min(25, 10 + 3 * len(triggers["Superlatives"]))
    if "Packaging" in triggers:
        score += min(8, 4 + len(triggers["Packaging"]))  # weak alone

    # Sector bonus (high-impact sectors with hype/claims)
    if "Sector Context" in triggers and (
        "Carbon Neutral" in triggers
        or "Offsets" in triggers
        or "Superlatives" in triggers
        or "Vague Claims" in triggers
    ):
        score += 15
        # extra synergy if superlatives present in those sectors
        if "Superlatives" in triggers:
            score += 8

    # 3) Evidence detector (gentle reduction; never below Medium if strong claims present)
    evidence_kinds = _evidence_strength(t_low)
    if evidence_kinds >= 3:
        score -= 18
    elif evidence_kinds == 2:
        score -= 12
    elif evidence_kinds == 1:
        score -= 6

    # 4) Zero-shot model nudges (kept modest; never dominates)
    clf = _clf()
    z = clf(text, CANDIDATE_LABELS, multi_label=True)
    labels: List[str] = list(z.get("labels", []))
    scores: List[float] = list(z.get("scores", []))

    # Top label for display
    if labels and scores:
        top_i = max(range(len(scores)), key=lambda i: scores[i])
        top_label, top_conf = labels[top_i], float(scores[top_i])
    else:
        top_label, top_conf = "no environmental claim", 1.0

    # Positive nudges
    score += 16.0 * _label_score(labels, scores, "greenwashing")
    score += 10.0 * _label_score(labels, scores, "vague environmental claim")
    score += 10.0 * _label_score(labels, scores, "offsetting claim")
    score += 5.0  * _label_score(labels, scores, "packaging claim")

    # Small negative nudge; cap so it never buries strong signals
    score -= min(6.0, 8.0 * _label_score(labels, scores, "specific substantiated claim"))

    # 5) Floors & clamps
    # If ad says "carbon neutral" but we don't see strong evidence, ensure score >= 70.
    strong_claim_present = "Carbon Neutral" in triggers or "Offsets" in triggers or "Superlatives" in triggers
    strong_evidence = evidence_kinds >= 3  # rough threshold
    if "Carbon Neutral" in triggers and not strong_evidence:
        score = max(score, 70.0)

    # Final clamp and level
    score = max(0.0, min(100.0, score))
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return {
        "score": int(round(score)),
        "level": level,
        "ai_label": top_label,
        "ai_confidence": round(top_conf * 100.0, 1),
        "triggers": triggers
    }
