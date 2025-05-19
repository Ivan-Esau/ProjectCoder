"""
Dieses Modul bietet eine Funktion zum Speichern generierter pytest-Tests
im `tests/`-Ordner des Projekts.
"""

from pathlib import Path


def save_tests(project_folder: str, file_path: str, tests_md: str) -> str:
    """
    Speichert Testcode (z. B. aus Markdown-Fences) als Datei `test_<modulname>.py`
    unter `<project_folder>/tests/`.

    Args:
        project_folder (str): Wurzelverzeichnis des Projekts.
        file_path (str): Relativer Pfad der zu testenden Moduldatei (z. B. "core/api_types.py").
        tests_md (str): Der Markdown-Inhalt mit den Testfunktionen.

    Returns:
        str: Der Pfad zur erzeugten Testdatei als String.
    """
    name = Path(file_path).stem
    p = Path(project_folder) / "tests" / f"test_{name}.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(tests_md, encoding="utf-8")
    return str(p)
