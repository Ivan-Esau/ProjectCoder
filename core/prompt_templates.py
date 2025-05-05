"""
core/prompt_templates.py

Dieses Modul definiert zentrale Prompt-Vorlagen für verschiedene
Dateitypen und Nutzungsszenarien:

- JSON_SCHEMA_NOTE: Prompt, um reines JSON zu generieren.
- TEST_FILE_NOTE: Prompt, um pytest-Tests für ein Modul zu erstellen.
- CODE_FILE_NOTE: Prompt, um Code-Dateien mit vollständigem Kontext und
  Ticketbeschreibung zu generieren.
"""

# Prompt-Vorlage für reine JSON-Ausgabe
JSON_SCHEMA_NOTE = (
    "Du bist ein JSON-Generator. "
    "Gib **allein** ein gültiges JSON-Objekt oder -Array zurück, "
    "ohne Code, Kommentare oder Markdown-Fences."
)

# Prompt-Vorlage für pytest-Testdateien
TEST_FILE_NOTE = (
    "Du bist ein pytest-Assistent. "
    "Erzeuge eine Testdatei für Modul `{module}`. "
    "Antworte **nur** mit `import …` und den `def test_…`-Funktionen, "
    "ohne weitere Kommentare, Erklärtexte oder Beispielimplementierungen."
)

# Prompt-Vorlage für vollständige Code-Dateien mit Kontext und Ticketbeschreibung
CODE_FILE_NOTE = (
    "Du bist ein reiner Code-Generator. "
    "Erhalte die komplette Datei `{file_path}` als Kontext:\n\n"
    "```{file_ext}\n"
    "{existing_code}\n"
    "```\n\n"
    "Ticket-Beschreibung:\n```{ticket_description}\n"
    "```\n\n"
    "Gib **die vollständige** Datei zurück, inkl. aller bisherigen Imports "
    "und Anpassungen gemäß Ticket. "
    "Antworte **nur** mit dem Code zwischen ```{file_ext} … ```."
)
