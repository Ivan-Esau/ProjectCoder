from pathlib import Path
from core.request_handler import send_llm_request

def generate_tests(api_url: str, api_key: str, ticket: dict, model: str) -> str:
    """
    Generiert Unit-Tests für ein gegebenes Ticket.
    Erwartet im Ticket-Dict die Keys file_path, title, beschreibung, anforderungen.
    """
    # Datei-Stammname ermitteln
    file_path = ticket["file_path"]  # KeyError, falls nicht vorhanden
    name = Path(file_path).stem
    # Prompt zusammenbauen
    prompt = (
        "Erstelle Unit-Tests für das Ticket.\n"
        f"Datei: {file_path}\n"
        f"Title: {ticket['title']}\n"
        f"Beschreibung: {ticket['beschreibung']}\n"
        f"Anforderungen:\n{ticket['anforderungen']}\n"
        f"Speichere die Tests in test_{name}.py"
    )
    # LLM aufrufen
    return send_llm_request(api_url, api_key, prompt, model)
