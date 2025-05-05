"""
storage/plan_storage.py

Dieses Modul bietet eine Funktion zum Speichern des Projektplans als Textdatei
unter `<project_folder>/docs/plan.txt`.
"""

from pathlib import Path


def save_plan(project_folder: str, plan_text: str) -> str:
    """
    Speichert den Projektplan in einer Textdatei in `docs/plan.txt`.

    Args:
        project_folder (str): Wurzelverzeichnis des Projekts.
        plan_text (str): Der vollständige Projektplan als mehrzeiliger Text.

    Returns:
        str: Der Pfad zur erzeugten Plan-Datei als String.
    """
    p = Path(project_folder) / "docs" / "plan.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(plan_text, encoding="utf-8")
    return str(p)
