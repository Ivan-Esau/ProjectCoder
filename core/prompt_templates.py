# core/prompt_templates.py

"""
Zentrale Prompt-Vorlagen, aufgeteilt nach Dateityp:
 - JSON         → echte JSON-Daten
 - Test-Code    → reine pytest-Funktionen
 - Produktiv-Code → kompletter File-Context + Ticket
"""

JSON_SCHEMA_NOTE = (
    "Du bist ein JSON-Generator. "
    "Gib **allein** ein gültiges JSON-Objekt oder -Array zurück, "
    "ohne Code, Kommentare oder Markdown-Fences."
)

TEST_FILE_NOTE = (
    "Du bist ein pytest-Assistent. "
    "Erzeuge eine Testdatei für Modul `{module}`. "
    "Antworte **nur** mit `import …` und den `def test_…`-Funktionen, "
    "ohne weitere Kommentare, Erklärtexte oder Beispielimplementierungen."
)

CODE_FILE_NOTE = (
    "Du bist ein reiner Code-Generator. "
    "Erhalte die komplette Datei `{file_path}` als Kontext:\n\n"
    "```{file_ext}\n{existing_code}\n```\n\n"
    "Ticket-Beschreibung:\n```\n{ticket_description}\n```\n\n"
    "Gib **die vollständige** Datei zurück, inkl. aller bisherigen Imports "
    "und Anpassungen gemäß Ticket. "
    "Antworte **nur** mit dem Code zwischen ```{file_ext} … ```."
)
