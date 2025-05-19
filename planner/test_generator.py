"""
Dieses Modul enthält Funktionen zum Generieren von Unit-Tests
für Code-Dateien basierend auf Ticket-Informationen.
"""

from pathlib import Path
from core.request_handler import send_llm_request


def generate_tests(
    api_url: str,
    api_key: str,
    ticket: dict,
    model: str
) -> str:
    """
    Generiert pytest-Unit-Tests für eine gegebene Ticket-Datei.

    Der Prompt enthält Dateipfad, Ticket-Titel, Beschreibung und Anforderungen,
    und fordert die Speicherung in einer Datei `test_<modulname>.py`.

    Args:
        api_url (str): Basis-URL des LLM-Endpunkts.
        api_key (str): API-Schlüssel für die Authentifizierung.
        ticket (dict): Ein Dictionary mit den Feldern:
            - "file_path" (str): Relativer Pfad zur Quellcode-Datei.
            - "title" (str): Titel des Tickets.
            - "beschreibung" (str): Textuelle Beschreibung des Tickets.
            - "anforderungen" (str): Technische Anforderungen oder Randbedingungen.
        model (str): Name des zu verwendenden Modells.

    Returns:
        str: Der generierte Testcode als String (mit `import …` und `def test_…`).

    Raises:
        KeyError: Wenn erwartete Felder im Ticket fehlen.
        requests.HTTPError: Bei HTTP-Fehlern im Request.
    """
    file_path = ticket["file_path"]
    name = Path(file_path).stem

    prompt = (
        "Erstelle Unit-Tests für das Ticket.\n"
        f"Datei: {file_path}\n"
        f"Title: {ticket['title']}\n"
        f"Beschreibung: {ticket['beschreibung']}\n"
        f"Anforderungen:\n{ticket['anforderungen']}\n"
        f"Speichere die Tests in test_{name}.py"
    )

    return send_llm_request(api_url, api_key, prompt, model)
