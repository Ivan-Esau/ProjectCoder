import json
from pathlib import Path
import pytest
from storage.saver import save_response

def test_save_response_in_project_logs(tmp_path):
    project_folder = tmp_path / "proj"
    user_input = "Eingabe1"
    response = "Antwort1"

    returned = save_response(str(project_folder), user_input, response)
    p = Path(returned)

    # Muss im logs-Ordner liegen
    assert p.parent.name == "logs"
    assert p.exists()

    # JSON laden und Inhalt prüfen
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["input"] == user_input
    assert data["response"] == response
    assert "timestamp" in data

def test_save_response_without_project_folder(tmp_path, monkeypatch):
    # Wenn project_folder leer, landet es in cwd/antworten
    monkeypatch.chdir(tmp_path)
    returned = save_response("", "X", "Y")
    p = Path(returned)
    assert p.parent.name == "antworten"
    assert p.exists()
