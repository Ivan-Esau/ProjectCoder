import json
from core.request_handler import send_llm_request

def generate_tickets(api_url: str, api_key: str, plan_text: str, model: str) -> list:
    """
    Erzeugt Tickets basierend auf einem Projektplan.
    Liefert ein Python-Objekt (Liste von Dicts).
    """
    # Baue Prompt
    prompt = (
        f"Basierend auf diesem Projektplan:\n{plan_text}\n"
        "Bitte liefere **nur** ein reines JSON-Array von Tickets, jedes mit den Feldern "
        "title, beschreibung, anforderungen und file_path."
    )
    # LLM aufrufen
    raw = send_llm_request(api_url, api_key, prompt, model)
    # Extrahiere JSON-Array
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
