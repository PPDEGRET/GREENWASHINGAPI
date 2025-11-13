import pytest
import os
from unittest.mock import patch, MagicMock
from openai import OpenAI

from src.app.services.gpt_service import _get_client, analyze_text_with_gpt


class TestGetClient:
    """Test cases for _get_client() function."""
    
    def test_get_client_raises_runtime_error_when_api_key_missing(self):
        """Test case 1: Verify that _get_client() raises a RuntimeError if OPENAI_API_KEY is not defined."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove OPENAI_API_KEY from environment
            os.environ.pop("OPENAI_API_KEY", None)
            
            with pytest.raises(RuntimeError) as exc_info:
                _get_client()
            
            assert "OPENAI_API_KEY is not set" in str(exc_info.value)
    
    def test_get_client_returns_openai_instance_when_api_key_present(self):
        """Test case 2: Verify that _get_client() returns an OpenAI client instance if OPENAI_API_KEY is defined."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-12345"}):
            client = _get_client()
            
            assert isinstance(client, OpenAI)
            assert client.api_key == "test-api-key-12345"


class TestAnalyzeTextWithGPT:
    """Test cases for analyze_text_with_gpt() function."""
    
    def test_analyze_text_returns_error_response_when_api_key_missing(self):
        """Test case 3: Verify that analyze_text_with_gpt returns a specific error response when OPENAI_API_KEY is missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove OPENAI_API_KEY from environment
            os.environ.pop("OPENAI_API_KEY", None)
            
            result = analyze_text_with_gpt("Sample text to analyze")
            
            assert result["risk_score"] == 0
            assert result["level"] == "Low"
            assert len(result["reasons"]) > 0
            assert "AI analysis skipped due to configuration error" in result["reasons"][0]
            assert "OPENAI_API_KEY" in result["reasons"][0]
    
    @patch('src.app.services.gpt_service._get_client')
    def test_analyze_text_uses_openai_client_when_api_key_present(self, mock_get_client):
        """Test case 4: Verify that analyze_text_with_gpt attempts to use the OpenAI client for actual analysis when the API key is present."""
        # Mock the OpenAI client and its response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"risk_score": 45, "level": "Medium", "reasons": ["Vague claims detected"]}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-12345"}):
            result = analyze_text_with_gpt("Our product is 100% eco-friendly")
            
            # Verify _get_client was called
            mock_get_client.assert_called_once()
            
            # Verify the OpenAI client's chat.completions.create was called
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            
            # Verify correct parameters were passed
            assert call_args.kwargs["model"] == "gpt-4o-mini"
            assert len(call_args.kwargs["messages"]) == 2
            assert call_args.kwargs["messages"][0]["role"] == "system"
            assert call_args.kwargs["messages"][1]["role"] == "user"
            assert "Our product is 100% eco-friendly" in call_args.kwargs["messages"][1]["content"]
            assert call_args.kwargs["response_format"] == {"type": "json_object"}
            assert call_args.kwargs["temperature"] == 0.2
            
            # Verify the result was parsed correctly
            assert result["risk_score"] == 45
            assert result["level"] == "Medium"
            assert "Vague claims detected" in result["reasons"]
    
    def test_analyze_text_returns_low_risk_for_empty_text(self):
        """Test that empty text returns a Low risk response."""
        result = analyze_text_with_gpt("")
        
        assert result["risk_score"] == 0
        assert result["level"] == "Low"
        assert "No text provided for analysis" in result["reasons"][0]
