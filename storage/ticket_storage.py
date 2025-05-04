import json
from pathlib import Path

def save_tickets(project_folder: str, tickets: list) -> str:
    p = Path(project_folder) / "tickets" / "tickets.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)
