import os
import json
from typing import Dict, Any

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env if present (no-op if missing)
load_dotenv()

def _get_client() -> OpenAI:
    """Create an OpenAI client lazily and fail with a clear message if the key is missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Create a .env with OPENAI_API_KEY=... or export it in your shell."
        )
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert in greenwashing detection, tasked with analyzing marketing materials based on EU regulations.
Your analysis should be critical, objective, and based on the provided text.

You must return a JSON object with the following schema:
{
  "risk_score": "integer (0-100)",
  "level": "'Low' or 'Medium' or 'High'",
  "reasons": "[string, ...]",
  "recommendations": "[string, ...]"
}

Where:
- "reasons" explains WHY the text may be greenwashing (or not), in short bullet-style statements.
- "recommendations" gives concrete suggestions to improve the ad and reduce greenwashing risk.

Scoring guide:
- 0-30 (Low): Claims are specific, verifiable, and backed by evidence.
- 31-70 (Medium): Claims are vague, ambiguous, or lack clear evidence.
- 71-100 (High): Claims are misleading, unsubstantiated, or use absolute statements without proof.
"""

def analyze_text_with_gpt(text: str) -> Dict[str, Any]:
    """
    Analyzes text for greenwashing risks using GPT.
    """
    if not text:
        return {"risk_score": 0, "level": "Low", "reasons": ["No text provided for analysis."]}

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze the following text for greenwashing risks:\n\n{text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        # The response content is a JSON string, so we parse it
        result = json.loads(response.choices[0].message.content)

        # Basic validation and normalization
        result["risk_score"] = int(result.get("risk_score", 0))
        result["level"] = result.get("level", "Low")
        result["reasons"] = result.get("reasons", [])
        result["recommendations"] = result.get("recommendations", [])

        return result

    except Exception as e:
        # Keep server running; surface a clear reason in the result
        print(f"Error during GPT analysis: {e}")
        return {
            "risk_score": 0,
            "level": "Low",
            "reasons": [
                "AI analysis skipped due to configuration error. Ensure OPENAI_API_KEY is set.",
            ],
        }
