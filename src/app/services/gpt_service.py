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
  "subtle_triggers": "[string, ...]",
  "recommendations": "[string, ...]"
}

Where:
- "reasons" are the main justifications for the score.
- "subtle_triggers" is a list of trigger keywords identified from the qualitative analysis (e.g., "omission", "jargon", "misleading_comparison").
- "recommendations" is a short list of concrete, user-facing suggestions to improve the claims (1–5 bullet points, concise).

Scoring guide:
- 0-30 (Low): Claims are specific, verifiable, and contextually clear.
- 31-70 (Medium): Claims are ambiguous, use jargon, or lack full context.
- 71-100 (High): Claims are misleading, rely on emotional appeals without proof, or omit critical information.
"""

from src.app.models.user import User

def _build_personalized_prompt(user: User) -> str:
    """Build a personalized system prompt based on user data."""
    prompt = SYSTEM_PROMPT

    prompt += "\n\n--- User Profile for Personalization ---\n"
    if user.sector:
        prompt += f"Industry Sector: {user.sector}\n"
        if "cosmetics" in user.sector.lower():
            prompt += "Focus: Pay special attention to the Green Claims Directive and rules on 'clean beauty' or 'natural' allegations.\n"
    if user.company_size:
        prompt += f"Company Size: {user.company_size}\n"
        if user.company_size in ["50-250", "250+"]:
            prompt += "Focus: Remind the user of CSRD/CSDDD reporting obligations where relevant.\n"
    if user.role:
        prompt += f"User's Role: {user.role}\n"
        if "marketing" in user.role.lower():
            prompt += "Tone: Provide recommendations oriented towards marketing wording and claim substantiation.\n"
        elif "legal" in user.role.lower() or "compliance" in user.role.lower():
            prompt += "Tone: Provide detailed legal citations and focus on regulatory compliance.\n"

    return prompt

def analyze_text_with_gpt(text: str, user: User) -> Dict[str, Any]:
    """Analyze text for greenwashing risks, qualitative triggers, and recommendations using GPT."""
    if not text:
        return {
            "risk_score": 0,
            "level": "Low",
            "reasons": ["No text provided for analysis."],
            "subtle_triggers": [],
            "recommendations": [],
        }

    personalized_prompt = _build_personalized_prompt(user)

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": personalized_prompt},
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
            "subtle_triggers": [],
            "recommendations": [],
        }
