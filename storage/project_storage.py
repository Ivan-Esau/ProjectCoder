import os
import re
from pathlib import Path
from datetime import datetime

def _slugify(name: str) -> str:
    """
    Wandelt einen beliebigen Projektnamen in einen URL-/Dateisystem-geeigneten Slug um.
    Falls nach Entfernung aller unerlaubten Zeichen nichts übrig bleibt, fällt auf 'projekt' zurück.
    """
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or 'projekt'

def create_project_structure(project_name: str, base_path: str = None) -> str:
    """
    Legt die Projektstruktur an unter
      <base_path>/ oder
      $PROJECT_BASE oder
      ./projects/
    mit Ordnern:
      docs/, src/, tests/, tickets/, logs/
    und Dateien README.md, pytest.ini.
    Gibt den absoluten Pfad des neuen Projektordners zurück.
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

    # README.md
    readme = project_folder / "README.md"
    readme.write_text(
        f"# {project_name}\n\nErstellt am {timestamp}\n",
        encoding="utf-8"
    )

    # pytest.ini
    pytest_ini = project_folder / "pytest.ini"
    pytest_ini.write_text(
        "[pytest]\nminversion = 6.0\n",
        encoding="utf-8"
    )

    return str(project_folder)
