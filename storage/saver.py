# storage/saver.py

import json
from datetime import datetime
from pathlib import Path
import os

def save_response(project_folder: str, user_input: str, response: str) -> str:
    """
    Speichert die Roh-Antwort der LLM zusammen mit Input und Timestamp
    in project_folder/logs/response_<timestamp>.json.
    Fallback: Wenn project_folder leer ist, dann in ./antworten/response_<timestamp>.json.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "timestamp": ts,
        "input":     user_input,
        "response":  response
    }

    # Fallback, wenn project_folder leer
    if not project_folder or not project_folder.strip():
        base_dir = Path(os.getcwd()) / "antworten"
    else:
        base_dir = Path(project_folder) / "logs"

    # Verzeichnisse anlegen
    base_dir.mkdir(parents=True, exist_ok=True)

    # Datei schreiben
    file_path = base_dir / f"response_{ts}.json"
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(file_path)
