import json
import re
from pathlib import Path
from typing import List, Dict, Any

class RulesEngine:
    def __init__(self, rules_path: Path):
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, rules_path: Path) -> List[Dict[str, Any]]:
        if not rules_path.exists():
            # In a real app, you'd probably want to log this or handle it more gracefully
            return []
        with open(rules_path, "r") as f:
            return json.load(f)

    def apply(self, text: str) -> List[Dict[str, Any]]:
        matches = []
        for rule in self.rules:
            try:
                if re.search(rule["pattern"], text, re.IGNORECASE):
                    matches.append(
                        {
                            "rule_id": rule["id"],
                            "category": rule["category"],
                            "severity": rule["severity"],
                            "matched_text": rule["pattern"], # a more advanced impl could find the actual text
                            "recommendation": rule["recommendation"],
                        }
                    )
            except re.error as e:
                # Log the error with the problematic rule pattern
                print(f"Regex error in rule {rule['id']} with pattern '{rule['pattern']}': {e}")
        return matches

# You can create a singleton instance for the app to use
# The path is relative to the project root, assuming the app runs from there.
RULES_FILE_PATH = Path("src/rules.json")
rules_engine = RulesEngine(RULES_FILE_PATH)
