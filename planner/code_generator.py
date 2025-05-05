"""
code_generator.py

Dieses Modul enthält Funktionen zum Generieren von Code-Dateien basierend auf
Tickets, in denen Datei-Pfad, Beschreibung und Anforderungen definiert sind.
"""

from pathlib import Path
from core.request_handler import send_llm_request


def generate_code_for_ticket(
    api_url: str,
    api_key: str,
    project_folder: str,
    ticket: dict,
    model: str
) -> str:
    """
    Generiert vollständigen Code für ein einzelnes Ticket.

    Der LLM-Prompt enthält Dateipfad, Ticket-Beschreibung und Anforderungen,
    sodass eine komplette Datei erstellt wird.

    Args:
        api_url (str): Basis-URL des LLM-Endpunkts (z. B. "https://api.openai.com/v1/chat/completions").
        api_key (str): API-Schlüssel für die Authentifizierung.
        project_folder (str): Pfad zum Stammverzeichnis des Projekts.
        ticket (dict): Ein Dictionary mit den Feldern:
            - "file_path" (str): Relativer Pfad zur Zieldatei.
            - "beschreibung" (str): Textuelle Beschreibung des Tickets.
            - "anforderungen" (str): Technische Anforderungen oder Randbedingungen.
        model (str): Name des zu verwendenden Modells (z. B. "gpt-4").

    Returns:
        str: Der vom LLM generierte Dateiinhalt als String.

    Raises:
        TypeError: Wenn `'file_path'` im Ticket fehlt oder None ist.
        requests.HTTPError: Bei HTTP-Fehlern im Request.
    """
    # Pfad und Dateiendung bestimmen
    file_path = ticket["file_path"]
    ext = Path(file_path).suffix.lower()
    lang = "Java" if ext == ".java" else "Python"

    # Prompt zusammenbauen
    prompt = (
        f"Implementiere folgendes Ticket in {lang}:\n"
        f"Datei: {file_path}\n"
        f"Beschreibung: {ticket['beschreibung']}\n"
        f"Anforderungen:\n{ticket['anforderungen']}"
    )

    # LLM-Aufruf
    return send_llm_request(api_url, api_key, prompt, model)
