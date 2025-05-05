# core/api_types.py

"""
Dieses Modul enthält Hilfsfunktionen zur Erkennung des Typs einer AI-API anhand ihrer Basis-URL.
"""

from urllib.parse import urlparse


def detect_api_type(api_url: str) -> str:
    """
    Ermittelt den API-Typ anhand der übergebenen URL.

    Unterstützte API-Typen:
      - "openai" : alle Sub-Domains von openai.com
      - "gemini" : generativelanguage.googleapis.com
      - "ollama" : Domains, die "ollama" oder "localhost" enthalten
      - "unknown": kein bekannter API-Typ erkannt

    Args:
        api_url (str): Die vollständige URL des API-Endpunkts.

    Returns:
        str: Der erkannte API-Typ ("openai", "gemini", "ollama" oder "unknown").
    """
    parsed = urlparse(api_url)
    host = parsed.netloc.lower()

    # Offenere Erkennung für OpenAI-Hosts
    if "openai.com" in host:
        return "openai"
    # Google Gemini läuft unter generativelanguage.googleapis.com
    if "generativelanguage.googleapis.com" in host:
        return "gemini"
    # Ollama-Server erkennen (auch lokale Instanzen)
    if "ollama" in host or "localhost" in host:
        return "ollama"

    return "unknown"
