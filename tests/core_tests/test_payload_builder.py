import pytest
from core.payload_builder import build_payload

@pytest.mark.parametrize("user_input, model, expected_model", [
    ("Hello", None, "gpt-3.5-turbo"),
    ("Hello", "custom-model", "custom-model"),
])
def test_build_payload_openai(user_input, model, expected_model):
    payload = build_payload("openai", user_input, model)
    # Standard-Schlüssel prüfen
    assert isinstance(payload, dict)
    assert payload["model"] == expected_model
    assert isinstance(payload["messages"], list)
    assert payload["messages"][0] == {"role": "user", "content": user_input}
    assert "temperature" in payload and isinstance(payload["temperature"], float)

def test_build_payload_gemini():
    user_input = "Test Gemini"
    payload = build_payload("gemini", user_input)
    assert isinstance(payload, dict)
    assert "contents" in payload and isinstance(payload["contents"], list)
    contents = payload["contents"][0]
    assert isinstance(contents, dict)
    assert "parts" in contents and isinstance(contents["parts"], list)
    part = contents["parts"][0]
    assert part == {"text": user_input}

@pytest.mark.parametrize("user_input, model, expected_model", [
    ("Hello", None, "llama2"),
    ("Hello", "my-llama", "my-llama"),
])
def test_build_payload_ollama(user_input, model, expected_model):
    payload = build_payload("ollama", user_input, model)
    assert isinstance(payload, dict)
    assert payload["model"] == expected_model
    assert payload["prompt"] == user_input

def test_build_payload_unknown():
    with pytest.raises(ValueError) as excinfo:
        build_payload("unknown_api", "input")
    assert "Unknown API type" in str(excinfo.value)
