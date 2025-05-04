import pytest
import json
from planner.ticket_generator import generate_tickets

@pytest.fixture(autouse=True)
def dummy_api(monkeypatch):
    """
    Stelle sicher, dass kein echter HTTP-Request abgesetzt wird:
    Wir patchen send_llm_request in jedem Test.
    """
    # Default stub, wird in den einzelnen Tests überschrieben
    monkeypatch.setattr(
        "planner.ticket_generator.send_llm_request",
        lambda api_url, api_key, prompt, model: ""
    )

def test_successful_parse_strips_fences_and_returns_list(monkeypatch):
    # Bereite ein JSON mit ```json-Fence und Text drumherum vor
    raw = (
        "Some intro\n"
        "```json\n"
        "[{\"title\":\"T1\",\"beschreibung\":\"B1\",\"anforderungen\":[],\"file_path\":\"f1\"}]\n"
        "```\n"
        "Some footer"
    )

    # Patch send_llm_request so dass es unser raw-String zurückgibt
    captured = {}
    def fake_send(api_url, api_key, prompt, model):
        captured.update(locals())
        return raw
    monkeypatch.setattr(
        "planner.ticket_generator.send_llm_request",
        fake_send
    )

    # Aufruf
    result = generate_tickets("url", "key", "PLAN_TEXT", "model-x")

    # Ergebnis ist geparstes JSON
    assert isinstance(result, list)
    assert result == [{"title": "T1", "beschreibung": "B1", "anforderungen": [], "file_path": "f1"}]

    # Prompt-Check: sollte Plan-Text und Hinweis enthalten
    assert "Basierend auf diesem Projektplan" in captured['prompt']
    assert "PLAN_TEXT" in captured['prompt']

def test_no_json_array_raises_value_error(monkeypatch):
    # Antwort ohne '['
    monkeypatch.setattr(
        "planner.ticket_generator.send_llm_request",
        lambda u,k,p,m: "keine json hier"
    )

    with pytest.raises(ValueError) as ei:
        generate_tickets("u", "k", "p", "m")
    msg = str(ei.value)
    assert "Kein JSON-Array" in msg
    assert "Roh-Antwort" in msg

def test_invalid_json_raises_value_error(monkeypatch):
    # Antwort mit eckigen Klammern, aber ungültigem JSON
    bad = "[{ invalid json }]"
    monkeypatch.setattr(
        "planner.ticket_generator.send_llm_request",
        lambda u,k,p,m: bad
    )

    with pytest.raises(ValueError) as ei:
        generate_tickets("u", "k", "p", "m")
    msg = str(ei.value)
    assert "Fehler beim Parsen" in msg
    # extrahiertes JSON sollte im Fehlertext auftauchen
    assert bad in msg

def test_trims_whitespace_before_matching(monkeypatch):
    # Antwort mit führenden/folgenden Whitespace und neuen Zeilen
    raw = "\n\n```json\n[  {\"a\":42}  ]\n```   "
    monkeypatch.setattr(
        "planner.ticket_generator.send_llm_request",
        lambda u,k,p,m: raw
    )

    result = generate_tickets("u","k","plan","m")
    assert result == [{"a": 42}]

def test_passes_correct_parameters_to_llm(monkeypatch):
    # Überprüfe, dass api_url, api_key, model weitergegeben werden
    captured = {}
    def fake_send(api_url, api_key, prompt, model):
        captured['api_url'] = api_url
        captured['api_key'] = api_key
        captured['model']   = model
        return "[{\"ok\":true}]"
    monkeypatch.setattr(
        "planner.ticket_generator.send_llm_request",
        fake_send
    )

    out = generate_tickets("my_url", "my_key", "mein Plan", "my_model")
    assert out == [{"ok": True}]
    assert captured['api_url'] == "my_url"
    assert captured['api_key'] == "my_key"
    assert captured['model']   == "my_model"
