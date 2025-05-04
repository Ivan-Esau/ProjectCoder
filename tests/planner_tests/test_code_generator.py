import pytest
from planner.code_generator import generate_code_for_ticket

def make_ticket(path, beschreibung="Desc", anforderungen=None):
    return {
        "file_path": path,
        "beschreibung": beschreibung,
        "anforderungen": anforderungen or ["Req1", "Req2"]
    }

@pytest.mark.parametrize("file_path, expected_lang", [
    ("src/module/foo.py",   "Python"),
    ("app/Main.java",       "Java"),
    ("lib/utilities.PY",    "Python"),  # case-insensitive suffix
    ("Game.JAVA",           "Java"),
])
def test_generate_code_for_ticket_chooses_language(monkeypatch, file_path, expected_lang):
    # Dummy code to return
    dummy_code = f"# This is {expected_lang} code"
    captured = {}

    def fake_send(api_url, api_key, prompt, model):
        captured['api_url']    = api_url
        captured['api_key']    = api_key
        captured['prompt']     = prompt
        captured['model']      = model
        return dummy_code

    # Patch the send_llm_request that's imported in code_generator
    monkeypatch.setattr("planner.code_generator.send_llm_request", fake_send)

    ticket = make_ticket(file_path, beschreibung="Implement X", anforderungen=["A","B"])
    result = generate_code_for_ticket(
        api_url="https://api.test",
        api_key="KEY123",
        project_folder="/tmp/proj",
        ticket=ticket,
        model="model-v1"
    )

    # send_llm_request wurde aufgerufen und das Dummy-Code zurückgegeben
    assert result == dummy_code

    # Prompt enthält den richtigen Language-Tag
    assert f"Implementiere folgendes Ticket in {expected_lang}:" in captured['prompt']
    # Prompt enthält Datei-Pfad und Beschreibung
    assert f"Datei: {file_path}" in captured['prompt']
    assert "Beschreibung: Implement X" in captured['prompt']
    # Nutzereingabe (model etc.) wurden weitergereicht
    assert captured['api_url'] == "https://api.test"
    assert captured['api_key'] == "KEY123"
    assert captured['model'] == "model-v1"

def test_generate_code_for_ticket_missing_file_path():
    # Wenn file_path fehlt oder None, Path(file_path).suffix wirft TypeError
    ticket = {"file_path": None, "beschreibung": "X", "anforderungen": ["A"]}
    with pytest.raises(TypeError):
        generate_code_for_ticket("url", "key", "/tmp", ticket, "m")
