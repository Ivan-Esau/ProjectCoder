"""
Dieses Modul stellt Funktionen zum Speichern von generiertem Code auf dem Dateisystem bereit.
Es extrahiert Code aus Markdown-Fences und legt die Quelldateien unter `<project_folder>/src/` ab.
"""

import re
from pathlib import Path


def _extract_code(markdown: str) -> str:
    """
    Extrahiert reinen Code aus einem Markdown-String, indem alle Code-Fences entfernt werden.

    Args:
        markdown (str): Der Markdown-Text, der Code in ```-Blöcken enthalten kann.

    Returns:
        str: Der extrahierte Code ohne Markdown-Fences, mit einheitlichen Zeilenenden (`\n`).
    """
    fence = re.compile(r"```[^\n]*\n([\s\S]*?)```", re.MULTILINE)
    blocks = fence.findall(markdown)
    code = "\n".join(blocks) if blocks else markdown
    return code.replace("\r\n", "\n")


def save_code(project_folder: str, file_path: str, code_md: str) -> str:
    """
    Speichert extrahierten Code aus Markdown in einer Datei unter `<project_folder>/src/<file_path>`.

    Dabei wird die Verzeichnisstruktur angelegt, falls sie noch nicht existiert.

    Args:
        project_folder (str): Wurzelverzeichnis des Projekts.
        file_path (str): Relativer Pfad (innerhalb von `src/`) zur Zieldatei, z. B. "core/api_types.py".
        code_md (str): Markdown-inhalt mit Code-Fences, aus denen der Code extrahiert wird.

    Returns:
        str: Der vollständige Pfad der geschriebenen Datei als String.
    """
    p = Path(project_folder) / "src" / file_path
    p.parent.mkdir(parents=True, exist_ok=True)
    code = _extract_code(code_md)
    p.write_text(code, encoding="utf-8")
    return str(p)
