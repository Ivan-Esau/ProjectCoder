import json
from pathlib import Path
import pytest
from storage.ticket_storage import save_tickets

def test_save_tickets_creates_json(tmp_path):
    project_folder = tmp_path / "proj"
    tickets = [
        {"title": "T1"},
        {"title": "T2"}
    ]

    returned = save_tickets(str(project_folder), tickets)
    p = Path(returned)
    # Pfad und Existenz
    assert p == project_folder / "tickets" / "tickets.json"
    assert p.exists()

    # JSON-Inhalt prüfen
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data == tickets
