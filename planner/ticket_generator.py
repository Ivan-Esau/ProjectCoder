"""
ticket_generator.py

Dieses Modul bietet Funktionen zum Erzeugen von Tickets
aus einem textuellen Projektplan mithilfe eines LLM.
"""

import json
from core.request_handler import send_llm_request


def generate_tickets(
    api_url: str,
    api_key: str,
    plan_text: str,
    model: str
) -> list:
    """
    Erzeugt eine Liste von Tickets basierend auf einem Projektplan.

    Der Prompt fordert den LLM auf, ein reines JSON-Array zurückzugeben,
    jedes Element mit den Feldern title, beschreibung, anforderungen und file_path.

    Args:
        api_url (str): Basis-URL des LLM-Endpunkts.
        api_key (str): API-Schlüssel für die Authentifizierung.
        plan_text (str): Der komplette Projektplan als Text.
        model (str): Name des zu verwendenden Modells.

    Returns:
        list: Eine Liste von Dictionaries, jeweils mit den Schlüsseln
              title, beschreibung, anforderungen und file_path.

    Raises:
        ValueError: Wenn kein JSON-Array in der Antwort gefunden wird
                    oder das Parsen des JSON fehlschlägt.
        requests.HTTPError: Bei HTTP-Fehlern im Request.
    """
    prompt = (
        f"Basierend auf diesem Projektplan:\n{plan_text}\n"
        "Bitte liefere **nur** ein reines JSON-Array von Tickets, "
        "jedes mit den Feldern title, beschreibung, anforderungen und file_path."
    )

    raw = send_llm_request(api_url, api_key, prompt, model)
    raw_str = raw.strip()
    start = raw_str.find('[')
    end = raw_str.rfind(']') + 1
    if start == -1 or end == 0:
        raise ValueError(f"Kein JSON-Array gefunden in Antwort. Roh-Antwort:\n{raw_str}")

    json_str = raw_str[start:end]
    try:
        tickets = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Fehler beim Parsen: {e}\nExtrahiertes JSON:\n{json_str}")

    return tickets
