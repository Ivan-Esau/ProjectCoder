import pytest
# 1) Importiere die Funktion aus dem Unterpaket
from planner.planner import generate_project_plan

def test_generate_project_plan_calls_llm(monkeypatch):
    captured = {}

    def fake_send(api_url, api_key, prompt, model):
        captured.update(locals())
        return "DUMMY_PLAN"

    # 2) Patch das korrekte Modul: planner.planner.send_llm_request
    monkeypatch.setattr(
        "planner.planner.send_llm_request",
        fake_send
    )

    proj_desc = "Entwickle eine Todo-App"
    result = generate_project_plan(
        api_url="https://api.example.com",
        api_key="APIKEY123",
        project_desc=proj_desc,
        model="test-model"
    )

    assert result == "DUMMY_PLAN"
    assert captured['api_url'] == "https://api.example.com"
    assert captured['api_key'] == "APIKEY123"
    assert captured['model']   == "test-model"
    assert "Erstelle eine detaillierte, schrittweise Projektplanung" in captured['prompt']
    assert proj_desc in captured['prompt']

def test_generate_project_plan_missing_description(monkeypatch):
    # 1) Import erneut aus planner.planner
    from planner.planner import generate_project_plan

    # 2) No-Op Stub, damit Du auf KeyError geprüft hast
    monkeypatch.setattr(
        "planner.planner.send_llm_request",
        lambda *args, **kwargs: "OK"
    )

    # Leerer Projekttext darf keinen Import-Fehler werfen
    result = generate_project_plan(
        api_url="url",
        api_key="key",
        project_desc="",   # empty
        model=None
    )
    assert result == "OK"
