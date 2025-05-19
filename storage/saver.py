"""
Dieses Modul speichert alle Roh-Antworten (Inputs und Outputs) der LLM-Aufrufe
mit Timestamp in JSON-Dateien unter `logs/` oder einem Fallback-Verzeichnis.
"""

import json
import os
from datetime import datetime
from pathlib import Path


def save_response(project_folder: str, user_input: str, response: str) -> str:
    """
    Speichert einen Datensatz mit Timestamp, dem Eingabetext und der LLM-Antwort.

    Die Datei wird abgelegt unter:
      `<project_folder>/logs/response_<YYYYMMDD_HHMMSS>.json`
    Falls `project_folder` leer oder ungültig ist, in `./antworten/`.

    Args:
        project_folder (str): Wurzelverzeichnis des Projekts oder leer.
        user_input (str): Der an die LLM gesendete Text.
        response (str): Die zurückgegebene LLM-Antwort.

    Returns:
        str: Der Pfad zur gespeicherten JSON-Datei als String.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "timestamp": ts,
        "input": user_input,
        "response": response
    }

    if not project_folder or not project_folder.strip():
        base_dir = Path(os.getcwd()) / "antworten"
    else:
        base_dir = Path(project_folder) / "logs"

    base_dir.mkdir(parents=True, exist_ok=True)
    file_path = base_dir / f"response_{ts}.json"
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(file_path)
