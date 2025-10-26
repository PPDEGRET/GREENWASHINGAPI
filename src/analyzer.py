# src/analyzer.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
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
CARBON_NEUTRAL_TERMS = [
    r"carbon[-\s]?neutral",
    r"climate[-\s]?neutral",
    r"co[₂²2][-\s]?neutral",
    r"net[-\s]?zero",
    r"netto[-\s]?null",
    r"netto[-\s]?nul",
    r"netto\s*nullstilling",
    r"netto\s*null",
    r"neutre\s+en\s+co2",
    r"neutre\s+en\s+carbone",
    r"neutralit[eé]\s+(?:en\s+)?carbone",
    r"neutralit[eé]\s+climatique",
    r"z[eé]ro\s+carbone",
    r"neutralidad\s+(?:de|en)\s+carbono",
    r"neutro\s+en\s+carbono",
    r"carbono\s+neutral",
    r"cero\s+emisiones",
    r"klima(?:t|)neutral(?:e|en|er|es|itet)?",
    r"klima[-\s]?neutral",
    r"klimaatneutraal(?:e|en)?",
    r"koolstofneutraal(?:e|en)?",
    r"neutro\s+in\s+carbonio",
    r"carbonio\s+neutro",
    r"neutralit[aà]\s+carbonica",
    r"impatto\s+zero",
    r"zero\s+emissioni",
    r"neutralidad\s+clim[aá]tica",
    r"klimaneutral",
    r"climate\s+positive",
    r"climatiquement\s+positif",
    r"clima\s+positivo",
    r"klimapositiv",
    r"positieve\s+klimaatimpact",
    r"positiv\s+klima\s*indsats",
    r"carbon[-\s]?free",
    r"zero\s*carbon",
    r"emisiones\s*cero",
    r"sin\s*carbono",
    r"senza\s*carbonio",
    r"ohne\s*co2",
    r"ohne\s*klimabelastning"
]

OFFSET_TERMS = [
    r"offset(?:ting)?",
    r"carbon\s*credits?",
    r"climate\s+compensation",
    r"compensat(?:e|ion)",
    r"insetting",
    r"compensaci[oó]n\s+de\s+carbono",
    r"cr[eé]ditos\s+de\s+carbono",
    r"compens\w*\s+carbono",
    r"neutralizar\s+carbono",
    r"compensation\s+carbone",
    r"cr[eé]dits?\s+carbone",
    r"compens\w*\s+carbone",
    r"kompensation",
    r"co[₂²2][-\s]?kompensation",
    r"klimakompensation",
    r"kompensatie",
    r"co[₂²2][-\s]?compensatie",
    r"kompenser\w*\s+(?:for\s+)?(?:co[₂²2]|udledning|emissioner)",
    r"kompens\w*\s+(?:co[₂²2]|udledning)",
    r"compenseer\w*\s+(?:co[₂²2]|uitstoot)",
    r"compensazione\s+di\s+carbonio",
    r"crediti\s+di\s+carbonio",
    r"compens\w*\s+carbonio",
    r"neutralizzazion[e]?\s+del\s+carbonio",
    r"neutralizzazion[e]?\s+di\s+co2",
    r"compensaciones\s+verdes",
    r"programa\s+de\s+compensaci[oó]n",
    r"bonos\s+de\s+carbono",
    r"carbon\s+offset\s+project",
    r"co2\s*kvoter",
    r"udligningsprojekter",
    r"udledning\s*skreditter",
    r"klima\s*kvoter",
    r"klimaat\s*compensatie",
    r"carbon\s*allowances",
    r"compensation\s+environnementale",
    r"neutralisation\s+des\s+\w*"
]

LIFECYCLE_TERMS = [
    r"life[-\s]?cycle",
    r"cycle\s+de\s+vie",
    r"ciclo\s+de\s+vida",
    r"ciclo\s+di\s+vita",
    r"lebenszyklus",
    r"livscyklus",
    r"levenscyclus",
]

OFFSET_TARGETS = [
    r"offset",
    r"credits?",
    r"compensation",
    r"compensaci[oó]n",
    r"compensazione",
    r"kompensation",
]

VAGUE_TERMS = [
    r"sustainable",
    r"green",
    r"eco\b",
    r"eco[-\s]?friendly",
    r"eco[-\s]?smart",
    r"eco[-\s]?aware",
    r"planet[-\s]?friendly",
    r"environmentally\s*friendly",
    r"earth[-\s]?friendly",
    r"planet\s+positive",
    r"nature[-\s]?positive",
    r"responsibly\s+sourced",
    r"responsibly\s+made",
    r"clean\s+ingredients",
    r"clean\s+beauty",
    r"clean\s+energy",
    r"climate\s+smart",
    r"green\s+energy",
    r"green\s+choice",
    r"eco\s+choice",
    r"durable",
    r"[eé]cologique",
    r"[eé]co[-\s]?responsable",
    r"respectueux\s+de\s+l'environnement",
    r"sans\s+impact",
    r"sans\s+compromis",
    r"bon\s+pour\s+la\s+plan[eè]te",
    r"vertueux",
    r"sostenible",
    r"[eé]col[oó]gico",
    r"amigable\s+con\s+(?:el\s+)?planeta",
    r"amigable\s+con\s+el\s+medio\s+ambiente",
    r"cuidado\s+del\s+planeta",
    r"respetuoso\s+con\s+el\s+planeta",
    r"verde\s+consciente",
    r"nachhaltig",
    r"umweltfreundlich",
    r"gr[uü]n",
    r"ressourcenschonend",
    r"klimaschonend",
    r"umweltschonend",
    r"nachhaltigere\s+wahl",
    r"bewusste\s+wahl",
    r"duurzaam",
    r"milieuvriendelijk",
    r"groene\s+keuze",
    r"verantwoord\s+geproduceerd",
    r"bewuste\s+keuze",
    r"bæredygtig",
    r"milj[oø]venlig",
    r"klimavenlig",
    r"grøn\s+profil",
    r"grøn\s+l[oø]sning",
    r"sostenibile",
    r"ecologico",
    r"rispettoso\s+dell'ambiente",
    r"amico\s+del\s+pianeta",
    r"scelta\s+verde",
    r"a\s+impatto\s+ridotto",
    r"filiera\s+responsabile",
    r"origine\s+responsabile",
    r"responsabilit[aà]\s+ambientale",
    r"ambientalmente\s+responsable",
    r"materiales\s+sostenibles",
    r"ingredientes\s+sostenibles",
    r"fabricaci[oó]n\s+responsable",
    r"eco\s+innovador",
    r"eco\s+eficiente",
    r"eco\s+consciente",
    r"produktion\s+med\s+omtanke"
]

ABSOLUTE_TERMS = [
    r"100%",
    r"always",
    r"never",
    r"zero\s*impact",
    r"impact\s*z[eé]ro",
    r"no\s*emissions",
    r"sans\s+\w*emission",
    r"completely",
    r"entirely",
    r"toujours",
    r"jamais",
    r"zu\s+null\s*emissionen?",
    r"ohne\s+emissionen",
    r"v[öo]llig\s+frei",
    r"garantiert\s+ohne",
    r"keine\s+klimawirkung",
    r"immer",
    r"niemals",
    r"aldrig",
    r"altid",
    r"siempre",
    r"nunca",
    r"sempre",
    r"mai",
    r"sin\s+emisiones",
    r"senza\s+emissioni",
    r"sin\s+impacto",
    r"sin\s+huella",
    r"huella\s+cero",
    r"garantizado",
    r"sin\s+riesgo",
    r"sin\s+dudas",
    r"mai\s+pi[uù]\s+inquinamento",
    r"totale",
    r"assolutamente",
    r"per\s+sempre",
    r"definitivamente",
    r"z[aá]rate\s+impacto"
]

COMPARATIVE_TERMS = [
    r"cleanest",
    r"greenest",
    r"most\s+sustainable",
    r"most\s+efficient",
    r"lowest\s*emissions",
    r"best\s+for\s+the\s+planet",
    r"ultimate",
    r"le\s+plus\s+(?:durable|[eé]cologique|vert)",
    r"le\s+meilleur\s+pour\s+la\s+plan[eè]te",
    r"am\s+(?:nachhaltigsten|umweltfreundlichsten|gr[uü]nsten)",
    r"die\s+beste\s+wahl\s+f[uü]r\s+den\s+planeten",
    r"meest\s+(?:duurzame|duurzaam|milieuvriendelijke|groene)",
    r"beste\s+voor\s+de\s+planeet",
    r"groenste\s+keuze",
    r"meest\s+bewuste",
    r"laagste\s+impact",
    r"mest\s+(?:bæredygtige|bæredygtig|milj[oø]venlige|grønne)",
    r"bedste\s+for\s+planeten",
    r"grønneste\s+valg",
    r"mindste\s+aftryk",
    r"pi[uù]\s+(?:sostenibile|ecologico|verde)",
    r"migliore\s+per\s+il\s+pi[aà]neta",
    r"massima\s+sostenibilit[aà]",
    r"minore\s+impatto",
    r"scelta\s+pi[uù]\s+verde",
    r"m[aá]s\s+(?:sostenible|ecol[oó]gico|verde)",
    r"mejor\s+para\s+el\s+planeta",
    r"impacto\s+m[aá]s\s+bajo",
    r"elecci[oó]n\s+m[aá]s\s+verde",
    r"impacto\s+reducido\s+al\s+m[aá]ximo",
    r"opci[oó]n\s+m[aá]s\s+sustentable"
]

PACKAGING_TERMS = [
    r"recyclable",
    r"recycled\s*plastic",
    r"biodegradable",
    r"compostable",
    r"sustainable\s*packaging",
    r"emballage\s+recyclable",
    r"emballage\s+durable",
    r"plastique\s+recycl[eé]",
    r"biod[eé]gradable",
    r"emballage\s+compostable",
    r"envase\s+reciclado",
    r"embalaje\s+reciclable",
    r"envase\s+compostable",
    r"material\s+reciclado",
    r"envase\s+sostenible",
    r"embalaje\s+sostenible",
    r"riciclabile",
    r"imballaggio\s+sostenibile",
    r"imballaggio\s+riciclabile",
    r"plastica\s+riciclata",
    r"riciclato",
    r"verpackung\s+recycelt",
    r"nachhaltige\s+verpackung",
    r"recycelte\s+verpackung",
    r"genanvendelig",
    r"genanvendelig\s+emballage",
    r"komposterbar",
    r"genbrugsmateriale",
    r"genbrugs\s*emballage",
    r"herbruikbaar",
    r"herbruikbare\s+verpakking",
    r"duurzame\s+verpakking",
    r"composteerbaar",
    r"circular\s+packaging",
    r"circular\s+design",
    r"emballage\s+reutilisable",
    r"emballage\s+reutilis[eé]",
    r"packaging\s+circulaire",
    r"material\s+biodegradable",
    r"envase\s+reutilizable",
    r"envase\s+biodegradable",
    r"envase\s+reciclado\s+postconsumo",
    r"plastica\s+riciclabile",
    r"imballaggio\s+riutilizzabile",
    r"imballaggio\s+circolare",
    r"packaging\s+senza\s+plastica",
    r"senza\s+plastica",
    r"plastikfrei",
    r"kunststofffrei",
    r"recycelbare\s+materialien",
    r"verpackung\s+ohne\s+plastik",
    r"genanvendt\s+plast",
    r"genanvendelige\s+materialer",
    r"genbrugelig",
    r"post-consumer\s+recycled"
]

def _compile_terms(terms: List[str]) -> re.Pattern:
    pattern = r"\b(?:" + "|".join(terms) + r")\b"
    return re.compile(pattern, re.I)

RX = {
    "carbon_neutral": _compile_terms(CARBON_NEUTRAL_TERMS),
    "offsets": _compile_terms(OFFSET_TERMS),
    "lifecycle_offset": re.compile(
        r"(?:" + "|".join(LIFECYCLE_TERMS) + r")" + r".+?(?:" + "|".join(OFFSET_TARGETS) + r")",
        re.I
    ),
    # Vague terms
    "vague_terms": _compile_terms(VAGUE_TERMS),
    # Absolutes
    "absolutes": _compile_terms(ABSOLUTE_TERMS),
    # Comparatives / superlatives frequently used for hype
    "comparatives": _compile_terms(COMPARATIVE_TERMS),
    # Packaging claims (supportive, weaker alone)
    "packaging": _compile_terms(PACKAGING_TERMS),
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

# Weighting constants (tweakable)
ALPHA = {
    "carbon_neutral": 0.65,
    "offsets": 0.45,
    "lifecycle_offset": 0.35,
    "absolutes": 0.30,
    "superlatives": 0.28,
    "vague": 0.22,
    "packaging_only": 0.12,
    "sector_interaction": 0.30,
    "offset_reliance": 0.25,
    "llm_greenwash": 0.18,
}

BETA = {
    "third_party": 0.60,
    "lca_epd": 0.50,
    "standards": 0.40,
    "scope": 0.35,
    "specificity": 0.45,
    "citation": 0.25,
}

# Specificity helpers
PERCENT_REDUCTION_RX = re.compile(r"\b\d{1,3}\s?%(\s*(reduction|lower|cut|moins))?\b", re.I)
BASELINE_YEAR_RX = re.compile(r"\b(baseline|from)\s*(19|20)\d{2}\b", re.I)
TARGET_YEAR_RX = re.compile(r"\b(by|to)\s*(20)\d{2}\b", re.I)

# -------------------------------
# Helpers
# -------------------------------
DEFAULT_RULE_WEIGHT = 0.65
DEFAULT_LLM_WEIGHT = 0.35


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

def clamp01(x: Any) -> float:
    try:
        return max(0.0, min(1.0, float(x or 0.0)))
    except (TypeError, ValueError):
        return 0.0


def noisy_or(risks: List[float]) -> float:
    p = 1.0
    for r in risks:
        p *= (1.0 - clamp01(r))
    return 1.0 - p


def compute_features(
    text: str,
    labels: Optional[List[str]] = None,
    scores: Optional[List[float]] = None,
) -> Dict[str, float]:
    t = text or ""
    features: Dict[str, float] = {}

    # Risk factors
    has_carbon_neutral = bool(RX["carbon_neutral"].search(t))
    features["f_carbon_neutral"] = 1.0 if has_carbon_neutral else 0.0

    offset_hits = RX["offsets"].findall(t)
    features["f_offsets"] = clamp01(len(offset_hits) / 3.0)

    features["f_lifecycle_offset"] = 1.0 if RX["lifecycle_offset"].search(t) else 0.0

    abs_hits = RX["absolutes"].findall(t)
    features["f_absolutes"] = clamp01(len(abs_hits) / 3.0)

    comp_hits = RX["comparatives"].findall(t)
    features["f_superlatives"] = clamp01(len(comp_hits) / 4.0)

    vague_hits = [match.lower() for match in RX["vague_terms"].findall(t)]
    features["f_vague"] = clamp01(len(set(vague_hits)) / 6.0)

    packaging_hits = RX["packaging"].findall(t)
    packaging_factor = clamp01(len(packaging_hits) / 4.0)
    has_other_claims = any(
        features[key] > 0.0
        for key in [
            "f_carbon_neutral",
            "f_offsets",
            "f_lifecycle_offset",
            "f_absolutes",
            "f_superlatives",
            "f_vague",
        ]
    )
    features["f_packaging_only"] = (
        packaging_factor if packaging_factor and not has_other_claims else 0.0
    )

    features["f_sector_risk"] = 1.0 if SECTOR_RX.search(t) else 0.0

    prob_greenwashing = 0.0
    if labels and scores:
        try:
            prob_greenwashing = _label_score(labels, scores, "greenwashing")
        except Exception:
            prob_greenwashing = 0.0
    features["f_llm_greenwash"] = clamp01(min(0.6, prob_greenwashing))

    # Evidence reducers
    features["e_third_party"] = 1.0 if EVIDENCE_RX["third_party"].search(t) else 0.0
    features["e_lca_epd"] = 1.0 if EVIDENCE_RX["epd_lca"].search(t) else 0.0

    standards_hits = sum(
        1 if EVIDENCE_RX[name].search(t) else 0
        for name in ("pas2060", "iso14021", "iso14067")
    )
    features["e_standards"] = clamp01(standards_hits / 2.0)

    scope_matches = {match.lower() for match in EVIDENCE_RX["scope"].findall(t)}
    features["e_scope"] = clamp01(len(scope_matches) / 3.0)

    has_percent = bool(PERCENT_REDUCTION_RX.search(t))
    has_baseline = bool(BASELINE_YEAR_RX.search(t))
    has_target = bool(TARGET_YEAR_RX.search(t))
    specificity_count = sum([has_percent, has_baseline, has_target])
    if specificity_count == 3:
        specificity = 1.0
    elif specificity_count == 2:
        specificity = 0.66
    elif specificity_count == 1:
        specificity = 0.33
    else:
        specificity = 0.0
    features["e_specificity"] = specificity

    citation_hits = EVIDENCE_RX["link"].findall(t)
    features["e_citation"] = clamp01(len(citation_hits) / 2.0)

    risk_keys = [
        "f_carbon_neutral",
        "f_offsets",
        "f_lifecycle_offset",
        "f_absolutes",
        "f_superlatives",
        "f_vague",
        "f_packaging_only",
        "f_sector_risk",
        "f_llm_greenwash",
    ]
    evidence_keys = [
        "e_third_party",
        "e_lca_epd",
        "e_standards",
        "e_scope",
        "e_specificity",
        "e_citation",
    ]
    features["n_risk_flags"] = float(
        sum(1 for key in risk_keys if features.get(key, 0.0) > 0.0)
    )
    features["n_evidence_flags"] = float(
        sum(1 for key in evidence_keys if features.get(key, 0.0) > 0.0)
    )

    return features


def leafcheck_score(features: Dict[str, float]) -> Dict[str, Any]:
    f_carbon = clamp01(features.get("f_carbon_neutral"))
    f_offsets = clamp01(features.get("f_offsets"))
    f_lifecycle = clamp01(features.get("f_lifecycle_offset"))
    f_absolutes = clamp01(features.get("f_absolutes"))
    f_superlatives = clamp01(features.get("f_superlatives"))
    f_vague = clamp01(features.get("f_vague"))
    f_packaging_only = clamp01(features.get("f_packaging_only"))
    f_sector = clamp01(features.get("f_sector_risk"))
    f_llm = clamp01(features.get("f_llm_greenwash"))

    e_third = clamp01(features.get("e_third_party"))
    e_lca = clamp01(features.get("e_lca_epd"))
    e_standards = clamp01(features.get("e_standards"))
    e_scope = clamp01(features.get("e_scope"))
    e_specificity = clamp01(features.get("e_specificity"))
    e_citation = clamp01(features.get("e_citation"))

    f_sector_interaction = clamp01(
        f_sector * (f_carbon + f_offsets + f_superlatives + f_vague) / 4.0
    )
    f_offset_reliance = clamp01(
        f_offsets * (1.0 - max(e_third, e_lca, e_standards))
    )

    risk_terms = {
        "carbon_neutral": ALPHA["carbon_neutral"] * f_carbon,
        "offsets": ALPHA["offsets"] * f_offsets,
        "lifecycle_offset": ALPHA["lifecycle_offset"] * f_lifecycle,
        "absolutes": ALPHA["absolutes"] * f_absolutes,
        "superlatives": ALPHA["superlatives"] * f_superlatives,
        "vague": ALPHA["vague"] * f_vague,
        "packaging_only": ALPHA["packaging_only"] * f_packaging_only,
        "sector_interaction": ALPHA["sector_interaction"] * f_sector_interaction,
        "offset_reliance": ALPHA["offset_reliance"] * f_offset_reliance,
        "llm_greenwash": ALPHA["llm_greenwash"] * f_llm,
    }

    risk_values = list(risk_terms.values())
    R_raw = noisy_or(risk_values)
    risk_strength = clamp01(sum(risk_values) / max(1, len(risk_values)))
    max_risk = clamp01(max(risk_values) if risk_values else 0.0)

    evidence_terms = {
        "third_party": BETA["third_party"] * e_third,
        "lca_epd": BETA["lca_epd"] * e_lca,
        "standards": BETA["standards"] * e_standards,
        "scope": BETA["scope"] * e_scope,
        "specificity": BETA["specificity"] * e_specificity,
        "citation": BETA["citation"] * e_citation,
    }

    E = sum(evidence_terms.values())
    evidence_values = list(evidence_terms.values())
    evidence_strength = clamp01(sum(evidence_values) / max(1, len(evidence_values)))

    contextual_risk = clamp01(0.65 * R_raw + 0.25 * risk_strength + 0.10 * max_risk)
    mitigation = clamp01(0.5 * evidence_strength)

    adjusted = clamp01(contextual_risk * (1.0 - mitigation))
    support_gap = clamp01(R_raw - mitigation)
    score_value = clamp01(0.7 * adjusted + 0.3 * support_gap)

    score = 100.0 * score_value

    if f_carbon == 1.0 and E < 0.5:
        score = max(score, 72.0)

    if R_raw > 0.65 and E >= 1.8:
        score = min(score, 68.0)

    score = max(0.0, min(100.0, score))

    if score >= 70.0:
        level = "High"
    elif score >= 40.0:
        level = "Medium"
    else:
        level = "Low"

    n_risk_flags = sum(1 for value in risk_terms.values() if value > 0.0)
    n_evidence_flags = sum(1 for value in evidence_terms.values() if value > 0.0)
    signal = clamp01(0.55 * risk_strength + 0.25 * max_risk + 0.20 * (1.0 - mitigation))
    conf = clamp01((n_risk_flags + n_evidence_flags) / 10.0 + 0.4 * signal)
    uncertainty = round(10.0 * (1.0 - conf), 2)

    breakdown = {
        "risk_terms": risk_terms,
        "evidence_terms": evidence_terms,
        "R_raw": R_raw,
        "risk_strength": risk_strength,
        "max_risk": max_risk,
        "evidence_sum": E,
        "evidence_strength": evidence_strength,
        "contextual_risk": contextual_risk,
        "mitigation": mitigation,
    }

    return {
        "score": int(round(score)),
        "level": level,
        "breakdown": breakdown,
        "uncertainty": uncertainty,
    }

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
            "triggers": {},
            "breakdown": {
                "risk_terms": {},
                "evidence_terms": {},
                "R_raw": 0.0,
                "risk_strength": 0.0,
                "max_risk": 0.0,
                "evidence_sum": 0.0,
                "evidence_strength": 0.0,
                "contextual_risk": 0.0,
                "mitigation": 0.0,
            },
            "uncertainty": 10.0,
        }

    t_low = text.lower()

    labels: List[str] = []
    scores: List[float] = []
    try:
        clf = _clf()
        result = clf(text, candidate_labels=CANDIDATE_LABELS, multi_label=True)
        labels = result.get("labels", [])
        scores = result.get("scores", [])
    except Exception:
        labels = []
        scores = []

    features = compute_features(t_low, labels, scores)
    scoring = leafcheck_score(features)
    triggers = _find_triggers(t_low)

    if labels and scores:
        top_i = max(range(len(scores)), key=lambda i: scores[i])
        top_label, top_conf = labels[top_i], float(scores[top_i])
    else:
        top_label, top_conf = "no environmental claim", 1.0

    return {
        "score": scoring["score"],
        "level": scoring["level"],
        "ai_label": top_label,
        "ai_confidence": round(top_conf * 100.0, 1),
        "triggers": triggers,
        "breakdown": scoring["breakdown"],
        "uncertainty": scoring.get("uncertainty", 0.0),
    }

def _resolve_level(score: float) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def blend_with_llm(
    rule_result: Dict[str, object],
    llm_result: Optional[Dict[str, object]],
    llm_weight: float = DEFAULT_LLM_WEIGHT,
) -> Dict[str, object]:
    """Combine LeafCheck rule score with an LLM judge score.

    Parameters
    ----------
    rule_result:
        Output of :func:`analyze_text`.
    llm_result:
        Dict with "risk_score"/"level" (as returned by :func:`judge_with_gpt`).
        If None or marked with ``{"_error": True}``, the rule score is returned.
    llm_weight:
        Contribution of the LLM score (0..1). The remaining weight is assigned to
        the rule score.
    """

    if not isinstance(rule_result, dict):
        raise TypeError("rule_result must be a dict returned by analyze_text")

    rule_score = float(rule_result.get("score", 0) or 0)
    base_level = str(rule_result.get("level", _resolve_level(rule_score)))

    if not llm_result or getattr(llm_result, "get", None) is None:
        return {
            "score": int(round(rule_score)),
            "level": _resolve_level(rule_score),
            "weights": {"rule": 1.0, "llm": 0.0},
            "rule_score": int(round(rule_score)),
            "rule_level": base_level,
            "llm_score": None,
            "llm_level": None,
            "llm_used": False,
        }

    if llm_result.get("_error"):
        return {
            "score": int(round(rule_score)),
            "level": _resolve_level(rule_score),
            "weights": {"rule": 1.0, "llm": 0.0},
            "rule_score": int(round(rule_score)),
            "rule_level": base_level,
            "llm_score": None,
            "llm_level": None,
            "llm_used": False,
            "warning": "LLM judge unavailable; using rule score only.",
        }

    llm_score = float(llm_result.get("risk_score", 0) or 0)
    llm_level = str(llm_result.get("level", _resolve_level(llm_score)))

    llm_weight = max(0.0, min(1.0, float(llm_weight)))
    rule_weight = 1.0 - llm_weight

    combined = rule_weight * rule_score + llm_weight * llm_score
    combined_level = _resolve_level(combined)

    return {
        "score": int(round(combined)),
        "level": combined_level,
        "weights": {"rule": round(rule_weight, 3), "llm": round(llm_weight, 3)},
        "rule_score": int(round(rule_score)),
        "rule_level": base_level,
        "llm_score": int(round(llm_score)),
        "llm_level": llm_level,
        "llm_used": True,
    }
