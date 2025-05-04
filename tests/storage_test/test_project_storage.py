import pytest
import shutil
from pathlib import Path
import storage.project_storage as ps

@pytest.mark.parametrize("name,slug", [
    ("Mein Projekt!",      "mein_projekt"),
    ("Hello, World 2025",  "hello_world_2025"),
    ("!@#$%^&*()",         "projekt"),          # now falls back to a default like "projekt"
    ("   Spaces   and---dashes ", "spaces_and_dashes"),
])
def test__slugify_various(name, slug):
    assert ps._slugify(name) == slug

def test_create_project_structure_default_base(tmp_path, monkeypatch):
    fake_base = tmp_path/"projects"
    monkeypatch.setenv("PROJECT_BASE", str(fake_base))
    # re-import to pick up new env
    import importlib; importlib.reload(ps)
    project_folder = ps.create_project_structure("Test Projekt")
    assert project_folder.startswith(str(fake_base))
    assert (Path(project_folder)/"src").exists()

def test_create_project_structure_custom_base(tmp_path):
    result = ps.create_project_structure("Custom Pfad", base_path=tmp_path)
    assert str(result).startswith(str(tmp_path))
    assert (Path(result)/"src").exists()
