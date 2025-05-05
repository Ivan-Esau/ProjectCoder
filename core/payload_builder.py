"""
core/payload_builder.py

Dieses Modul stellt eine Funktion zum Erstellen des Request-Payloads
für verschiedene AI-APIs bereit (OpenAI, Gemini, Ollama).
"""

from typing import Optional, Dict, Any


def build_payload(
    api_type: str,
    user_input: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Baut das API-Payload für den angegebenen API-Typ zusammen.

    Unterstützte API-Typen:
      - "openai"  : Payload enthält 'model', 'messages' und 'temperature'.
      - "gemini"  : Payload enthält 'contents'.
      - "ollama"  : Payload enthält 'model' und 'prompt'.

    Args:
        api_type (str): Typ der API ("openai", "gemini", "ollama").
        user_input (str): Eingabetext, der an die AI übergeben wird.
        model (Optional[str]): Optionaler Modellname; falls None, wird das Standardmodell verwendet.

    Returns:
        Dict[str, Any]: Ein Dictionary mit den API-spezifischen Parametern.

    Raises:
        ValueError: Wenn der api_type unbekannt ist.
    """
    if api_type == "openai":
        return {
            "model": model or "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": user_input}],
            "temperature": 0.7
        }
    elif api_type == "gemini":
        return {
            "contents": [
                {
                    "parts": [
                        {"text": user_input}
                    ]
                }
            ]
        }
    elif api_type == "ollama":
        return {
            "model": model or "llama2",
            "prompt": user_input
        }
    else:
        raise ValueError(f"Unknown API type: {api_type}")
