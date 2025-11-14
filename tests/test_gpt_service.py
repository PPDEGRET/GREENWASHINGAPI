import pytest
import os
from unittest.mock import patch, MagicMock
import uuid
from src.app.models.user import User
from src.app.services.gpt_service import _get_client, analyze_text_with_gpt


class TestGetClient:
    """Test cases for _get_client() function."""
    
    def test_get_client_raises_runtime_error_when_api_key_missing(self):
        """Test case 1: Verify that _get_client() raises a RuntimeError if OPENAI_API_KEY is not defined."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(RuntimeError) as exc_info:
                _get_client()
            assert "OPENAI_API_KEY is not set" in str(exc_info.value)
    
    @patch('src.app.services.gpt_service.OpenAI')
    def test_get_client_returns_openai_instance_when_api_key_present(self, mock_openai):
        mock_instance = MagicMock()
        mock_instance.api_key = "test-api-key-12345"
        mock_openai.return_value = mock_instance

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-12345"}):
            client = _get_client()
            mock_openai.assert_called_once_with(api_key="test-api-key-12345")
            assert client is mock_instance


class TestAnalyzeTextWithGPT:
    """Test cases for analyze_text_with_gpt() function."""

    @pytest.fixture
    def mock_user(self):
        return User(id=uuid.uuid4(), email="test@example.com", is_premium=False)

    def test_analyze_text_returns_error_response_when_api_key_missing(self, mock_user):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            result = analyze_text_with_gpt("Sample text to analyze", mock_user)
            assert result["risk_score"] == 0
            assert result["level"] == "Low"
            assert "AI analysis skipped" in result["reasons"][0]

    @patch('src.app.services.gpt_service._get_client')
    def test_analyze_text_uses_openai_client_when_api_key_present(self, mock_get_client, mock_user):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"risk_score": 45, "level": "Medium", "reasons": ["Vague claims detected"]}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-12345"}):
            result = analyze_text_with_gpt("Our product is 100% eco-friendly", mock_user)
            
            mock_get_client.assert_called_once()
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            
            assert call_args.kwargs["model"] == "gpt-4o-mini"
            assert "Our product is 100% eco-friendly" in call_args.kwargs["messages"][1]["content"]
            
            assert result["risk_score"] == 45
            assert result["level"] == "Medium"

    def test_analyze_text_returns_low_risk_for_empty_text(self, mock_user):
        result = analyze_text_with_gpt("", mock_user)
        assert result["risk_score"] == 0
        assert result["level"] == "Low"
        assert "No text provided" in result["reasons"][0]
