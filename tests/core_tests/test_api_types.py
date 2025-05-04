import pytest
from core.api_types import detect_api_type

@pytest.mark.parametrize("url, expected", [
    # OpenAI-Endpunkte
    ("https://api.openai.com/v1/chat/completions", "openai"),
    ("http://openai.com/foo",                   "openai"),

    # Gemini-Endpunkte
    ("https://generativelanguage.googleapis.com/v1beta/models", "gemini"),
    ("http://generativelanguage.googleapis.com/anything",        "gemini"),

    # Ollama-/Localhost-Endpunkte
    ("http://localhost:8080/v1/models",        "ollama"),
    ("https://ollama.ai/models",                "ollama"),
    ("http://my-ollama-server.local/api",       "ollama"),

    # Unbekannte URLs
    ("https://example.com/api",     "unknown"),
    ("",                            "unknown"),
    ("ftp://generativelanguage.COM", "unknown"),  # Case-Sensitivity check
])
def test_detect_api_type(url, expected):
    assert detect_api_type(url) == expected
