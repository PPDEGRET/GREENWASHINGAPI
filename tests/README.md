# Unit Tests

This directory contains unit tests for the GreenCheck API.

## Setup

Install test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run specific test file:

```bash
pytest tests/test_gpt_service.py
```

Run specific test case:

```bash
pytest tests/test_gpt_service.py::TestGetClient::test_get_client_raises_runtime_error_when_api_key_missing
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Test Coverage

### `test_gpt_service.py`

Tests for the GPT service module:

1. **test_get_client_raises_runtime_error_when_api_key_missing**: Verifies that `_get_client()` raises a RuntimeError if OPENAI_API_KEY is not defined.
2. **test_get_client_returns_openai_instance_when_api_key_present**: Verifies that `_get_client()` returns an OpenAI client instance if OPENAI_API_KEY is defined.
3. **test_analyze_text_returns_error_response_when_api_key_missing**: Verifies that `analyze_text_with_gpt` returns a specific error response when OPENAI_API_KEY is missing.
4. **test_analyze_text_uses_openai_client_when_api_key_present**: Verifies that `analyze_text_with_gpt` attempts to use the OpenAI client for actual analysis when the API key is present.
5. **test_analyze_text_returns_low_risk_for_empty_text**: Verifies that empty text returns a Low risk response.

### `test_main.py`

Tests for the main application module:

1. **test_main_loads_dotenv_at_startup**: Verifies that `main.py` successfully loads environment variables using load_dotenv() at startup.
2. **test_main_module_imports_successfully**: Verifies that the main module can be imported without errors.
