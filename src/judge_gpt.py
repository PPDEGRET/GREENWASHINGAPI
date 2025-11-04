# src/judge_gpt.py
from __future__ import annotations
import json
from typing import Any, Dict

# OpenAI SDK v1
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # handled at runtime

from config import MissingEnvironmentVariable, get_settings


SYSTEM_PROMPT = """You are a careful EU green-claims reviewer.
Assess marketing text for potential greenwashing risk under EU-style rules
(e.g., Green Claims initiative, Unfair Commercial Practices, substantiation principles).
Be conservative if claims are absolute (e.g., "carbon neutral", "cleanest/greenest") without concrete scope/evidence.
Return a JSON object with fields:
- risk_score: integer 0-100 (0 = no risk, 100 = extreme risk)
- level: "Low"|"Medium"|"High"
- reasons: short bullet list (2-5 items), no line breaks
Scoring hints:
- "carbon neutral", "net zero", "offsets/credits" without PAS 2060/ISO 14021/14067, LCA/EPD, third-party verification -> High (>=70)
- "cleanest/greenest/most sustainable" or superlatives w/o scope/evidence -> Medium/High
- Specific, scoped, quantifiable claims with clear third-party verification can reduce to Low/Medium.
"""

USER_TEMPLATE = """AD TEXT:
<<<
{ad_text}
>>>

Instructions:
1) Read the full text.
2) Apply EU-style green-claims logic.
3) Output strict JSON with keys: risk_score, level, reasons.
"""


def _client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("OpenAI SDK not installed. Add `openai` to requirements.txt and rebuild the image.")
    api_key = get_settings().openai_api_key
    if not api_key:
        raise MissingEnvironmentVariable("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def judge_with_gpt(ad_text: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Returns dict: {"risk_score": int, "level": str, "reasons": [str,str,...]}
    Raises RuntimeError on configuration issues (caught by caller).
    """
    ad_text = (ad_text or "").strip()
    if not ad_text:
        return {"risk_score": 0, "level": "Low", "reasons": ["No claim text provided."]}

    client = _client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TEMPLATE.format(ad_text=ad_text)},
    ]

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        content = resp.choices[0].message.content
        data = json.loads(content) if content else {}
        # Normalize
        score = int(max(0, min(100, int(data.get("risk_score", 0)))))
        level = str(data.get("level", "Low")).title()
        reasons = data.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]
        reasons = [str(r) for r in reasons if r]
        return {"risk_score": score, "level": level, "reasons": reasons}
    except MissingEnvironmentVariable:
        message = "Missing OpenAI API key. Set OPENAI_API_KEY in your secrets and retry."
        return {
            "risk_score": 0,
            "level": "Low",
            "reasons": ["LLM judge skipped: missing OPENAI_API_KEY."],
            "_error": True,
            "_error_message": message,
        }
    except Exception as e:
        # Graceful fallback
        detail = f"{type(e).__name__}: {e}"
        message = "GPT review failed. See the details below and retry once the issue is resolved."
        return {
            "risk_score": 0,
            "level": "Low",
            "reasons": [f"LLM judge failed: {detail}"],
            "_error": True,
            "_error_message": message,
        }
