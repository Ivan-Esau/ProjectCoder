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
    Generiert vollständigen Code für ein Ticket.
    Übergibt der LLM einen einfachen Prompt, um komplette Datei zu erzeugen.
    """
    # Pfad und Sprache bestimmen
    file_path = ticket["file_path"]  # TypeError, falls None
    ext = Path(file_path).suffix.lower()
    lang = "Java" if ext == ".java" else "Python"
    # Prompt zusammenbauen
    prompt = (
        f"Implementiere folgendes Ticket in {lang}:\n"
        f"Datei: {file_path}\n"
        f"Beschreibung: {ticket['beschreibung']}\n"
        f"Anforderungen:\n{ticket['anforderungen']}"
    )
    # LLM aufrufen
    return send_llm_request(api_url, api_key, prompt, model)
