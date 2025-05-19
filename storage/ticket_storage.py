"""
Dieses Modul speichert generierte Tickets als JSON-Array-Datei
unter `<project_folder>/tickets/tickets.json`.
"""

import json
from pathlib import Path


def save_tickets(project_folder: str, tickets: list) -> str:
    """
    Speichert eine Liste von Ticket-Dictionaries im JSON-Format.

    Args:
        project_folder (str): Wurzelverzeichnis des Projekts.
        tickets (list): Liste von Dictionaries, jedes mit den Schlüsseln
                        `title`, `beschreibung`, `anforderungen`, `file_path`.

    Returns:
        str: Der Pfad zur gespeicherten `tickets.json`-Datei als String.
    """
    p = Path(project_folder) / "tickets" / "tickets.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)
