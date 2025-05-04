import pytest
from core.request_handler import send_llm_request

class DummyResponse:
    def __init__(self, json_data, status_exception=None):
        self._json = json_data
        self._status_exception = status_exception

    def raise_for_status(self):
        if self._status_exception:
            raise self._status_exception

    def json(self):
        return self._json

def test_send_llm_request_with_api_key(monkeypatch):
    calls = {}
    # Stub für requests.post
    def fake_post(url, headers, json):
        calls['url'] = url
        calls['headers'] = headers
        calls['json'] = json
        # Simuliere eine OpenAI-Antwortstruktur
        return DummyResponse({
            "choices": [
                {"message": {"content": "Antwort vom LLM"}}
            ]
        })

    # Patch requests.post in unserem Modul
    monkeypatch.setattr("core.request_handler.requests.post", fake_post)

    result = send_llm_request(
        api_url="https://api.openai.com/v1/chat/completions",
        api_key="mein-test-key",
        user_input="Hallo Welt",
        model="test-model"
    )

    # Rückgabewert korrekt weitergereicht?
    assert result == "Antwort vom LLM"

    # URL korrekt übergeben?
    assert calls['url'] == "https://api.openai.com/v1/chat/completions"

    # Authorization-Header gesetzt?
    assert calls['headers']["Authorization"] == "Bearer mein-test-key"
    assert calls['headers']["Content-Type"] == "application/json"

    # Payload entspricht build_payload für openai
    expected_payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Hallo Welt"}],
        "temperature": 0.7
    }
    assert calls['json'] == expected_payload

def test_send_llm_request_without_api_key(monkeypatch):
    calls = {}
    # Stub für requests.post
    def fake_post(url, headers, json):
        calls['headers'] = headers
        # Simuliere eine Gemini-Antwortstruktur
        return DummyResponse({
            "candidates": [
                {"content": {"parts": [{"text": "Gemini-Antwort"}]}}
            ]
        })

    monkeypatch.setattr("core.request_handler.requests.post", fake_post)

    result = send_llm_request(
        api_url="https://generativelanguage.googleapis.com/v1beta/models/foo:generateContent",
        api_key="",
        user_input="Test",
        model=None
    )

    # Rückgabe der Gemini-Antwort
    assert result == "Gemini-Antwort"

    # Wenn kein api_key angegeben, darf es keinen Authorization-Header geben
    assert "Authorization" not in calls['headers']
    assert calls['headers']["Content-Type"] == "application/json"

def test_send_llm_request_http_error(monkeypatch):
    # Simuliere, dass raise_for_status() eine HTTPError wirft
    class HTTPError(Exception):
        pass

    def fake_post(url, headers, json):
        return DummyResponse({"irrelevant": True}, status_exception=HTTPError("404 Not Found"))

    monkeypatch.setattr("core.request_handler.requests.post", fake_post)

    with pytest.raises(Exception) as excinfo:
        send_llm_request(
            api_url="https://api.openai.com/v1/chat/completions",
            api_key="key",
            user_input="x",
            model="m"
        )
    assert "404 Not Found" in str(excinfo.value)
