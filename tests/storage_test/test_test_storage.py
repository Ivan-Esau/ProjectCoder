from pathlib import Path
import pytest
from storage.test_storage import save_tests

def test_save_tests_creates_file(tmp_path):
    project_folder = tmp_path / "proj"
    file_path = "pkg/module.py"
    tests_md = "# Testcode"

    returned = save_tests(str(project_folder), file_path, tests_md)
    p = Path(returned)
    # Pfad korrekt
    assert p == project_folder / "tests" / "test_module.py"
    assert p.exists()

    # Inhalt stimmt
    assert p.read_text(encoding="utf-8") == tests_md
