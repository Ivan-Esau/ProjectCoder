"""
core/response_parser.py

Dieses Modul stellt eine Funktion bereit, um die Roh-Antworten verschiedener
AI-APIs (OpenAI, Gemini, Ollama) in ein einheitliches Format (Text oder strukturierte Daten)
umzuwandeln.
"""

from typing import Any, Dict


def parse_response(api_type: str, response_json: Dict[str, Any]) -> Any:
    """
    Parsed die JSON-Antwort einer AI-API und extrahiert den eigentlichen Inhalt.

    Unterstützte API-Typen:
      - "openai" : Erwartet ein 'choices'-Array mit einer 'message.content'
      - "gemini" : Erwartet ein 'candidates'-Array mit 'content.parts[0].text'
      - "ollama" : Erwartet ein Feld 'response'
      - sonst     : Gibt die gesamte JSON-Antwort als String zurück

    Im Fehlerfall (z. B. unerwartete Struktur) wird eine Fehlermeldung
    im Format "[Parse error]: <Fehlertext>" zurückgegeben.

    Args:
        api_type (str): Der API-Typ, wie von `detect_api_type` ermittelt.
        response_json (Dict[str, Any]): Die rohe JSON-Antwort der API.

    Returns:
        Any: Der extrahierte Antwortinhalt (in der Regel String), oder
             im Fehlerfall eine Fehlermeldungs-String.

    """
    try:
        if api_type == "openai":
            # Bei Chat-Completions: Inhalt der ersten Wahl zurückgeben
            return response_json["choices"][0]["message"]["content"]
        elif api_type == "gemini":
            # Bei Gemini: Text der ersten Kandidaten-Antwort
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        elif api_type == "ollama":
            # Bei Ollama: Feld 'response' zurückgeben
            return response_json["response"]
        else:
            # Fallback: gesamte Response als String
            return str(response_json)
    except Exception as e:
        # Parse-Fehler abfangen und als Nachricht zurückliefern
        return f"[Parse error]: {e}"
