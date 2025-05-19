"""
Dieses Modul bietet Funktionen zur Generierung von Projektplänen
auf Basis einer textuellen Projektbeschreibung.
"""

from core.request_handler import send_llm_request


def generate_project_plan(
    api_url: str,
    api_key: str,
    project_desc: str,
    model: str
) -> str:
    """
    Erzeugt eine detaillierte, schrittweise Projektplanung für ein gegebenes Projekt.

    Der Prompt fordert den LLM auf, klare Überschriften und nummerierte Schritte zu nutzen.

    Args:
        api_url (str): Basis-URL des LLM-Endpunkts.
        api_key (str): API-Schlüssel für die Authentifizierung.
        project_desc (str): Textuelle Beschreibung des Projekts.
        model (str): Name des zu verwendenden Modells.

    Returns:
        str: Der generierte Projektplan als Text.

    Raises:
        requests.HTTPError: Bei HTTP-Fehlern im Request.
    """
    prompt = (
        "Erstelle eine detaillierte, schrittweise Projektplanung für folgendes Projekt:\n"
        f"{project_desc}\n"
        "Nutze klare Überschriften und nummerierte Schritte."
    )
    return send_llm_request(api_url, api_key, prompt, model)
