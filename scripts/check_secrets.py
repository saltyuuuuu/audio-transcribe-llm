from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"ark-[A-Za-z0-9-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"LTAI[A-Za-z0-9]{12,}"),
]
SKIP_DIRS = {".git", ".venv", "__pycache__", "generated-configs"}
SKIP_FILES = {".env"}


def should_scan(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    if parts & SKIP_DIRS:
        return False
    if path.name in SKIP_FILES:
        return False
    return path.is_file() and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".pyc"}


def main() -> int:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PATTERNS:
            for match in pattern.finditer(text):
                hits.append(f"{path.relative_to(ROOT)}: {match.group(0)[:8]}...")
    if hits:
        print("Potential secrets found:")
        print("\n".join(hits))
        return 1
    print("No obvious secrets found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

