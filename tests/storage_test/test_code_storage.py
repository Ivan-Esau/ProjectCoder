import os
import pytest
from storage.code_storage import _extract_code, save_code

@pytest.mark.parametrize("markdown,expected", [
    # Kein Fence → Rückgabe unverändert
    ("print('hello')", "print('hello')"),
    # Einfacher Fence
    ("```python\nx=1\ny=2\n```", "x=1\ny=2\n"),
    # Mehrere Fences werden zusammengefügt
    ("Intro\n```py\nfoo\n```\nText\n```js\nbar\n```\nEnde",
     "foo\n\nbar\n"),
    # Windows-CRLF werden zu LF normalisiert
    ("```txt\r\nline1\r\nline2\r\n```", "line1\nline2\n"),
])
def test__extract_code_various(markdown, expected):
    assert _extract_code(markdown) == expected

def test__extract_code_no_fence_returns_markdown():
    md = "```not a fence```"
    # Da kein Zeilenumbruch folgt, matcht der Regex nicht und gibt originalen String zurück
    assert _extract_code(md) == md

def test_save_code_creates_file(tmp_path):
    project_folder = tmp_path / "myproject"
    file_path = "pkg/module.py"
    # Markdown mit Fence
    code_md = "Einführung\n```py\nprint('ok')\n```\nFußnote"

    saved = save_code(str(project_folder), file_path, code_md)

    # Pfad stimmt
    expected_path = project_folder / "src" / file_path
    assert saved == str(expected_path)
    assert expected_path.exists()

    # Inhalt ist korrekt extrahiert und geschrieben
    content = expected_path.read_text(encoding="utf-8")
    assert content == "print('ok')\n"

def test_save_code_overwrites_existing(tmp_path):
    project_folder = tmp_path / "proj"
    file_path = "a.py"
    first_md = "```py\nA\n```"
    second_md = "```py\nB\n```"

    # Erstes Save
    p1 = save_code(str(project_folder), file_path, first_md)
    # Zweites Save sollte überschreiben
    p2 = save_code(str(project_folder), file_path, second_md)

    assert p1 == p2
    content = (project_folder / "src" / file_path).read_text(encoding="utf-8")
    assert content == "B\n"
