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
You are an expert in environmental communication and greenwashing detection, compliant with EU regulations.
Your role is to analyze marketing text and identify SUBTLE greenwashing tactics that a simple rule-based system might miss.

Focus ONLY on qualitative aspects like:
- **Omissions / Cherry-picking:** Highlighting a minor positive aspect while ignoring a major negative one.
- **Misleading Comparisons:** Presenting a relative benefit as an absolute one.
- **Vague or Unproven Jargon:** Using technical-sounding terms without clear, verifiable explanations.
- **Emotional Storytelling:** Using evocative language to imply a large positive impact without evidence.
- **Over-generalization:** Suggesting a whole product is 'green' when only one component is.

Do NOT focus on simple keywords like "100% green", "eco-friendly", "net-zero", as a rule-based system already handles those.

You MUST return a JSON object with the following schema:
{
  "risk_score": "integer (0-100)",
  "level": "'Low' or 'Medium' or 'High'",
  "reasons": "[string, ...]",
  "subtle_triggers": "[string, ...]"
}

Where:
- "reasons" are the main justifications for the score.
- "subtle_triggers" is a list of trigger keywords identified from the qualitative analysis (e.g., "omission", "jargon", "misleading_comparison").

Scoring guide:
- 0-30 (Low): Claims are specific, verifiable, and contextually clear.
- 31-70 (Medium): Claims are ambiguous, use jargon, or lack full context.
- 71-100 (High): Claims are misleading, rely on emotional appeals without proof, or omit critical information.
"""

def analyze_text_with_gpt(text: str) -> Dict[str, Any]:
    """
    Analyzes text for greenwashing risks and subtle qualitative triggers using GPT.
    """
    if not text:
        return {"risk_score": 0, "level": "Low", "reasons": ["No text provided for analysis."], "subtle_triggers": []}

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze the following text for greenwashing risks and subtle triggers:\n\n{text}"}
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
        result["subtle_triggers"] = result.get("subtle_triggers", [])

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
