from pathlib import Path

def save_plan(project_folder: str, plan_text: str) -> str:
    p = Path(project_folder) / "docs" / "plan.txt"
    # Erstelle docs/, falls es noch nicht existiert
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(plan_text, encoding="utf-8")
    return str(p)
