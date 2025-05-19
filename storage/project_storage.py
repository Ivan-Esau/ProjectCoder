"""
Dieses Modul verwaltet das Anlegen neuer Projektordner mit
Standardstruktur und Grunddateien wie README und pytest.ini.
"""

import os
import re
from pathlib import Path
from datetime import datetime


def _slugify(name: str) -> str:
    """
    Wandelt einen beliebigen Projektnamen in einen Dateisystem-sicheren Slug um.

    Erlaubte Zeichen sind a–z und 0–9; alle anderen werden durch Unterstriche ersetzt.
    Führende, folgende oder doppelte Unterstriche werden bereinigt.
    Falls das Ergebnis leer ist, wird 'projekt' zurückgegeben.

    Args:
        name (str): Der ursprüngliche Projektname.

    Returns:
        str: Der bereinigte Slug.
    """
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or 'projekt'


def create_project_structure(project_name: str, base_path: str = None) -> str:
    """
    Legt eine neue Ordnerstruktur für ein Projekt an und erzeugt README.md sowie pytest.ini.

    Die Struktur:
      <root>/
        docs/
        src/
        tests/
        tickets/
        logs/

    Root-Verzeichnis wird ermittelt aus:
      1. base_path-Parameter
      2. Umgebungsvariable PROJECT_BASE
      3. Standard: `<current_working_directory>/projects`

    Der Projektordner erhält den Namen `<slug>_<YYYYMMDD_HHMMSS>`.

    Args:
        project_name (str): Der lesbare Name des Projekts.
        base_path (str, optional): Optionaler Basis-Pfad für alle Projekte.

    Returns:
        str: Der absolute Pfad zum neu erstellten Projektordner.
    """
    # Basis-Verzeichnis ermitteln
    if base_path:
        root = Path(base_path)
    elif os.getenv("PROJECT_BASE"):
        root = Path(os.getenv("PROJECT_BASE"))
    else:
        root = Path.cwd() / "projects"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(project_name)
    project_folder = root / f"{slug}_{timestamp}"

    # Ordnerstruktur anlegen
    for sub in ["docs", "src", "tests", "tickets", "logs"]:
        (project_folder / sub).mkdir(parents=True, exist_ok=True)

    # README.md anlegen
    readme = project_folder / "README.md"
    readme.write_text(
        f"# {project_name}\n\nErstellt am {timestamp}\n",
        encoding="utf-8"
    )

    # pytest.ini anlegen
    pytest_ini = project_folder / "pytest.ini"
    pytest_ini.write_text(
        "[pytest]\nminversion = 6.0\n",
        encoding="utf-8"
    )

    return str(project_folder)
