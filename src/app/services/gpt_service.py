import os
import json
from openai import OpenAI
from typing import Dict, Any

# It's better to load the API key once and reuse the client
# The API key can be set as an environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert in greenwashing detection, tasked with analyzing marketing materials based on EU regulations.
Your analysis should be critical, objective, and based on the provided text.

You must return a JSON object with the following schema:
{
  "risk_score": "integer (0-100)",
  "level": "'Low' or 'Medium' or 'High'",
  "reasons": "[string, ...]"
}

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

        return result

    except Exception as e:
        print(f"Error during GPT analysis: {e}")
        return {
            "risk_score": 0,
            "level": "Low",
            "reasons": ["An error occurred during AI analysis."],
        }
