import pytest
from core.response_parser import parse_response

def test_parse_response_openai():
    resp_json = {
        "choices": [
            {"message": {"content": "OpenAI-Antwort"}}
        ]
    }
    assert parse_response("openai", resp_json) == "OpenAI-Antwort"

def test_parse_response_gemini():
    resp_json = {
        "candidates": [
            {"content": {"parts": [{"text": "Gemini-Antwort"}]}}
        ]
    }
    assert parse_response("gemini", resp_json) == "Gemini-Antwort"

def test_parse_response_ollama():
    resp_json = {"response": "Ollama-Antwort"}
    assert parse_response("ollama", resp_json) == "Ollama-Antwort"

def test_parse_response_unknown_type():
    # Sollte einfach das gesamte Objekt als String zurückgeben
    obj = {"foo": "bar"}
    result = parse_response("something_else", obj)
    assert result == str(obj)

def test_parse_response_malformed_key(monkeypatch):
    # Ein leeres Dict löst einen KeyError aus und testet so den Error-Pfad
    bad_json = {}
    result = parse_response("openai", bad_json)
    assert result.startswith("[Parse error]:")

def test_parse_response_non_dict(monkeypatch):
    # Wenn response_json kein dict ist, wird str(response_json) verwendet oder ein Parse error
    resp = "not a dict"
    result = parse_response("openai", resp)
    # Da resp["choices"] sofort einen TypeError wirft, fangen wir das ab
    assert result.startswith("[Parse error]:")
