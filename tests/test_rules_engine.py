import json
import unittest
from pathlib import Path
from src.app.services.rules_engine import RulesEngine

class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.rules_content = [
            {
                "id": "test_rule_1",
                "category": "Test Category",
                "pattern": "test pattern",
                "severity": "High",
                "recommendation": "Test recommendation"
            }
        ]
        self.rules_path = Path("test_rules.json")
        with open(self.rules_path, "w") as f:
            json.dump(self.rules_content, f)

    def tearDown(self):
        self.rules_path.unlink()

    def test_apply_rules(self):
        engine = RulesEngine(self.rules_path)
        text = "This is a test pattern."
        matches = engine.apply(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["rule_id"], "test_rule_1")

if __name__ == "__main__":
    unittest.main()
