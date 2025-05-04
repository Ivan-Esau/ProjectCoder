import pytest
from pathlib import Path
from storage.plan_storage import save_plan

def test_save_plan_creates_file_and_returns_path(tmp_path):
    project_folder = tmp_path / "proj"
    plan_text = "Das ist mein Projektplan."

    # Aufruf
    returned = save_plan(str(project_folder), plan_text)

    # Erwarteter Pfad
    expected = project_folder / "docs" / "plan.txt"
    assert returned == str(expected)
    assert expected.exists()

    # Inhalt prüfen
    content = expected.read_text(encoding="utf-8")
    assert content == plan_text
