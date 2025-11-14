import unittest
from unittest.mock import patch, MagicMock
from src.app.services.analysis_service import AnalysisService
from src.app.services.rules_engine import rules_engine

class TestAnalysisService(unittest.TestCase):

    @patch('src.app.services.analysis_service.analyze_text_with_gpt')
    @patch('src.app.services.analysis_service.extract_text_from_image')
    def test_analysis_pipeline(self, mock_extract_text, mock_analyze_gpt):
        # 1. Setup - Configure mocks
        mock_extract_text.return_value = "This is a test claim about being eco-friendly."

        mock_analyze_gpt.return_value = {
            "risk_score": 50,
            "level": "Medium",
            "reasons": ["GPT reason"],
            "subtle_triggers": [],
            "recommendations": ["GPT recommendation"]
        }

        # We can use the actual rules_engine for this test, or mock it if we want to isolate more.
        # Let's use the real one to make the test more integrated.
        analysis_service = AnalysisService(rules_engine)

        # 2. Act - Run the analysis
        image_bytes = b"test_image_bytes"  # The content doesn't matter as OCR is mocked
        result = analysis_service.analyze_image(image_bytes)

        # 3. Assert - Check the results
        self.assertIsNotNone(result)

        # Check that our mocks were called
        mock_extract_text.assert_called_once_with(image_bytes)
        mock_analyze_gpt.assert_called_once_with("This is a test claim about being eco-friendly")

        # Check the aggregated score and level.
        # Rule score: "eco-friendly" is in rule_001, let's say that gives a score of 10.
        # GPT score: 50
        # Combined: (10 * 0.3) + (50 * 0.7) = 3 + 35 = 38
        # Risk level for 38 is 'Low'. Let's adjust mock gpt score to get Medium

        mock_analyze_gpt.return_value = { "risk_score": 70, "level": "Medium", "reasons": [], "recommendations": []}
        result = analysis_service.analyze_image(image_bytes)
        # Recalculate: (10 * 0.3) + (70 * 0.7) = 3 + 49 = 52. This is "Medium".
        self.assertEqual(result["level"], "Medium")
        self.assertEqual(result["score"], 52)

        # Check that reasons and recommendations are combined
        self.assertIn("Misleading Terminology", result["reasons"])
        self.assertIn("Avoid absolute terms. Quantify the environmental benefit (e.g., 'made with 50% recycled materials').", result["recommendations"])

if __name__ == "__main__":
    unittest.main()
