from planner.test_generator import generate_tests
import pytest

def make_ticket(file_path, title="My Ticket", beschreibung="Beschreibung", anforderungen=None):
    return {
        "file_path": file_path,
        "title": title,
        "beschreibung": beschreibung,
        "anforderungen": anforderungen or ["Req1", "Req2"]
    }

def test_generate_tests_calls_llm(monkeypatch):
    # Sammle die Parameter, die an send_llm_request übergeben werden
    captured = {}
    dummy_response = "def test_dummy():\n    assert True"
    def fake_send(api_url, api_key, prompt, model):
        captured['api_url'] = api_url
        captured['api_key'] = api_key
        captured['prompt'] = prompt
        captured['model'] = model
        return dummy_response

    # Patch das LLM-Interface im Modul test_generator
    monkeypatch.setattr("planner.test_generator.send_llm_request", fake_send)

    ticket = make_ticket(
        file_path="module.py",
        title="Ticket Titel",
        beschreibung="Eine kurze Beschreibung",
        anforderungen=["A", "B"]
    )
    result = generate_tests("https://api.test", "KEY123", ticket, "test-model")

    # Rückgabe
    assert result == dummy_response

    # Parameter-Checks
    assert captured['api_url'] == "https://api.test"
    assert captured['api_key'] == "KEY123"
    assert captured['model'] == "test-model"

    # Prompt-Inhalt
    assert "Erstelle Unit-Tests für das Ticket" in captured['prompt']
    assert "Title: Ticket Titel" in captured['prompt']
    assert "Beschreibung: Eine kurze Beschreibung" in captured['prompt']
    assert "Anforderungen:\n['A', 'B']" in captured['prompt']
    # Überprüfung, dass der Dateiname im Prompt korrekt eingebunden wurde
    assert "test_module.py" in captured['prompt']

def test_generate_tests_missing_file_path_key():
    # Wenn file_path gar nicht existiert, sollte ein KeyError geworfen werden
    ticket = {"title": "T", "beschreibung": "B", "anforderungen": ["R"]}
    with pytest.raises(KeyError):
        generate_tests("url", "key", ticket, "model")
