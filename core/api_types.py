"""
core/api_types.py

Dieses Modul enthält Hilfsfunktionen zur Erkennung des Typs einer AI-API anhand ihrer Basis-URL.
"""

from urllib.parse import urlparse


def detect_api_type(api_url: str) -> str:

    parsed = urlparse(api_url)
    host = parsed.netloc.lower()

    # Überprüfe, ob die Host-Domain zu einer bekannten API gehört
    if "api.openai.com" in host:
        return "openai"
    if "api.gemini.google.com" in host:
        return "gemini"
    if "ollama.com" in host:
        return "ollama"

    # Fallback, falls kein bekannter Typ erkannt wurde
    return "unknown"
