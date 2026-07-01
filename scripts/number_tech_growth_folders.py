# -*- coding: utf-8 -*-
"""Number top-level 技术成长/ section folders and fix links."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"d:\学习")

FOLDER_RENAMES: list[tuple[str, str]] = [
    ("技术成长/Java", "技术成长/01-Java"),
    ("技术成长/数据与中间件", "技术成长/02-数据与中间件"),
    ("技术成长/运维与部署", "技术成长/03-运维与部署"),
    ("技术成长/计算机基础", "技术成长/04-计算机基础"),
    ("技术成长/AI工程", "技术成长/05-AI工程"),
    ("技术成长/C++嵌入式", "技术成长/06-C++嵌入式"),
    ("技术成长/扩展语言", "技术成长/07-扩展语言"),
]

# Full-path replacements (longest first)
PATH_REPLACEMENTS = [
    ("技术成长/07-扩展语言/", "技术成长/07-扩展语言/"),
    ("技术成长/06-C++嵌入式/", "技术成长/06-C++嵌入式/"),
    ("技术成长/05-AI工程/", "技术成长/05-AI工程/"),
    ("技术成长/04-计算机基础/", "技术成长/04-计算机基础/"),
    ("技术成长/03-运维与部署/", "技术成长/03-运维与部署/"),
    ("技术成长/02-数据与中间件/", "技术成长/02-数据与中间件/"),
    ("技术成长/01-Java/", "技术成长/01-Java/"),
]

# Relative segment: only when not already numbered (01-Java etc.)
RELATIVE_PATTERNS: list[tuple[str, str]] = [
    (r"(?<!\d-)(?<=[\./])扩展语言/", "07-扩展语言/"),
    (r"(?<!\d-)(?<=[\./])C\+\+嵌入式/", "06-C++嵌入式/"),
    (r"(?<!\d-)(?<=[\./])AI工程/", "05-AI工程/"),
    (r"(?<!\d-)(?<=[\./])计算机基础/", "04-计算机基础/"),
    (r"(?<!\d-)(?<=[\./])运维与部署/", "03-运维与部署/"),
    (r"(?<!\d-)(?<=[\./])数据与中间件/", "02-数据与中间件/"),
    (r"(?<!\d-)(?<=[\./])Java/", "01-Java/"),
]


def git_mv(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"SKIP missing: {src}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["git", "mv", str(src), str(dst)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        shutil.move(str(src), str(dst))
    print(f"mv: {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")


def apply_renames() -> None:
    for old_rel, new_rel in FOLDER_RENAMES:
        git_mv(ROOT / old_rel.replace("/", "\\"), ROOT / new_rel.replace("/", "\\"))


def fix_text(text: str) -> str:
    for old, new in PATH_REPLACEMENTS:
        text = text.replace(old, new)
    for pattern, repl in RELATIVE_PATTERNS:
        text = re.sub(pattern, repl, text)
    return text


def fix_links() -> int:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".ps1", ".json", ".css", ".html"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        updated = fix_text(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def main() -> None:
    apply_renames()
    n = fix_links()
    print(f"\nUpdated {n} files.")


if __name__ == "__main__":
    main()
