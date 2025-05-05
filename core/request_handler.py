"""
core/request_handler.py

Dieses Modul stellt eine Funktion bereit, um eine Anfrage an eine AI-API zu senden,
indem es den API-Typ ermittelt, das passende Payload baut, den HTTP-Request absetzt
und die Antwort parst.
"""

import requests
from core.api_types import detect_api_type
from core.payload_builder import build_payload
from core.response_parser import parse_response


def send_llm_request(
    api_url: str,
    api_key: str,
    user_input: str,
    model: str
):
    """
    Sendet eine Anfrage an die angegebene LLM-API und gibt die geparste Antwort zurück.

    Der Ablauf:
      1. Erkennung des API-Typs (openai, gemini, ollama).
      2. Bau des API-spezifischen Payloads.
      3. Absenden des HTTP-POST-Requests.
      4. Fehlerbehandlung bei HTTP-Statuscodes >= 400.
      5. Parsen der Roh-Antwort in ein einheitliches Format.

    Args:
        api_url (str): Basis-URL des API-Endpunkts (z. B. "https://api.openai.com/v1/chat/completions").
        api_key (str): API-Schlüssel für die Authentifizierung. Wenn leer, wird keine Authorization-Header gesetzt.
        user_input (str): Der Eingabetext, der an das LLM gesendet wird.
        model (str): Modellname, der im Payload verwendet werden soll (z. B. "gpt-4" oder "llama2").

    Returns:
        Any: Die von `parse_response` zurückgegebene, verarbeitete Antwort (z. B. reiner Text oder strukturierte Daten).

    Raises:
        requests.HTTPError: Wenn der HTTP-Statuscode des API-Responses auf einen Fehler hinweist.
        ValueError: Wenn `detect_api_type` oder `build_payload` auf unbekannte Typen stößt.
        KeyError / TypeError: Wenn das erwartete Format der API-Antwort nicht vorliegt.
    """
    # 1. API-Typ ermitteln
    api_type = detect_api_type(api_url)

    # 2. Payload bauen
    payload = build_payload(api_type, user_input, model)

    # 3. Header zusammenstellen
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # 4. Anfrage senden und auf HTTP-Fehler prüfen
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()

    # 5. Antwort parsen und zurückgeben
    return parse_response(api_type, response.json())
