import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.app.main import app  # Assuming your FastAPI app instance is in main
from src.app.schemas.analysis import AnalysisResponse, RecommendationItem

@pytest.fixture
def client():
    return TestClient(app)

def test_analyze_image_endpoint_success(client):
    """
    Tests the /analyze endpoint with a mock analysis service to ensure it
    returns the expected structured response.
    """
    # Mock the entire analysis_service.analyze_image function
    mock_recommendation = RecommendationItem(
        type="avoid_absolute",
        message="Avoid absolute environmental claims...",
        severity=3,
        triggered_by=["superlatives"]
    )
    mock_analysis_result = AnalysisResponse(
        score=85,
        level="High",
        reasons=["Vague language used."],
        text="Eco-friendly product 100% sustainable.",
        recommendations=[mock_recommendation]
    )

    with patch('src.app.routers.analysis.analyze_image', return_value=mock_analysis_result.dict()) as mock_analyze:
        # Use a dummy file for the upload
        dummy_file = ("test.png", b"fake-image-bytes", "image/png")

        response = client.post("/api/v1/analyze", files={"file": dummy_file})

        # Assertions
        assert response.status_code == 200
        json_response = response.json()

        assert json_response["score"] == 85
        assert json_response["level"] == "High"
        assert "Vague language used." in json_response["reasons"]
        assert "recommendations" in json_response
        assert len(json_response["recommendations"]) == 1

        # Verify the structure of the recommendation item
        recommendation = json_response["recommendations"][0]
        assert recommendation["type"] == "avoid_absolute"
        assert recommendation["severity"] == 3
        assert "superlatives" in recommendation["triggered_by"]

        # Ensure the mocked service was called
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
