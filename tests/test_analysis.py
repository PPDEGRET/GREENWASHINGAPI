import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.app.main import app
from src.app.schemas.analysis import AnalysisResponse, RuleMatch, GPTAnalysis

@pytest.fixture
def client():
    return TestClient(app)

def test_analyze_image_endpoint_success(client):
    """
    Tests the /analyze endpoint with a mock analysis service to ensure it
    returns the expected structured response.
    """
    mock_analysis_result = {
        "score": 52,
        "level": "Medium",
        "reasons": ["Misleading Terminology"],
        "recommendations": ["Avoid absolute terms..."],
        "rule_matches": [
            {
                "rule_id": "rule_001",
                "category": "Misleading Terminology",
                "severity": "High",
                "matched_text": "eco-friendly",
                "recommendation": "Avoid absolute terms..."
            }
        ],
        "gpt_analysis": {
            "risk_score": 70,
            "level": "Medium",
            "reasons": ["GPT reason"],
            "subtle_triggers": [],
            "recommendations": ["GPT recommendation"]
        }
    }

    with patch('src.app.routers.analysis.analysis_service.analyze_image', return_value=mock_analysis_result) as mock_analyze, \
         patch('src.app.services.usage_service.can_perform_analysis', return_value=True), \
         patch('src.app.services.usage_service.log_analysis'):

        dummy_file = ("test.png", b"fake-image-bytes", "image/png")
        response = client.post("/api/v1/analyze", files={"file": dummy_file})

        assert response.status_code == 200
        json_response = response.json()

        assert json_response["score"] == 52
        assert json_response["level"] == "Medium"
        assert "Misleading Terminology" in json_response["reasons"]
        assert "rule_matches" in json_response
        assert len(json_response["rule_matches"]) == 1
        assert json_response["rule_matches"][0]["rule_id"] == "rule_001"
        assert "gpt_analysis" in json_response
        assert json_response["gpt_analysis"]["risk_score"] == 70

        mock_analyze.assert_called_once()

def test_analyze_image_endpoint_not_image(client):
    """
    Tests that a non-image file upload is correctly rejected with a 400 error.
    """
    dummy_file = ("test.txt", b"not-an-image", "text/plain")
    response = client.post("/api/v1/analyze", files={"file": dummy_file})
    assert response.status_code == 400
    assert "File provided is not an image." in response.json()["detail"]

def test_analyze_image_endpoint_empty_file(client):
    """
    Tests that an empty file upload is correctly rejected with a 400 error.
    """
    dummy_file = ("test.png", b"", "image/png")
    response = client.post("/api/v1/analyze", files={"file": dummy_file})
    assert response.status_code == 400
    assert "Uploaded file is empty." in response.json()["detail"]
