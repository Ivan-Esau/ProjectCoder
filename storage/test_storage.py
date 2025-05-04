from pathlib import Path

def save_tests(project_folder: str, file_path: str, tests_md: str) -> str:
    name = Path(file_path).stem
    p = Path(project_folder) / "tests" / f"test_{name}.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(tests_md, encoding="utf-8")
    return str(p)
