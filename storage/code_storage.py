from pathlib import Path
import re

def _extract_code(markdown: str) -> str:
    fence = re.compile(r"```[^\n]*\n([\s\S]*?)```", re.MULTILINE)
    blocks = fence.findall(markdown)
    code = "\n".join(blocks) if blocks else markdown
    return code.replace("\r\n", "\n")

def save_code(project_folder: str, file_path: str, code_md: str) -> str:
    p = Path(project_folder) / "src" / file_path
    p.parent.mkdir(parents=True, exist_ok=True)
    code = _extract_code(code_md)
    p.write_text(code, encoding="utf-8")
    return str(p)
