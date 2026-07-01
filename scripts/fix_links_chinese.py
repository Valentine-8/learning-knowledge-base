# -*- coding: utf-8 -*-
"""Strip redundant 技术成长/ prefixes and fix broken migration links."""
from pathlib import Path

ROOT = Path(r"d:\学习")

REPLACEMENTS = [
    ("../../技术成长/00-通用/01-面试方法论/06-面试与晋升素材库.md", "./面试与晋升素材库.md"),
    ("../../技术成长/00-通用/04-求职追踪.md", "./求职追踪.md"),
    ("../../../../技术成长/", "../../../"),
    ("../../../技术成长/", "../../"),
    ("../../技术成长/", "../"),
    ("技术成长/00-通用/01-面试方法论/06-面试与晋升素材库.md", "技术成长/00-通用/面试与晋升素材库.md"),
    ("技术成长/00-通用/04-求职追踪.md", "技术成长/00-通用/求职追踪.md"),
    ("../03-求职面试/简历.md", "../Java/简历.md"),
    ("03-Database/02-MySQL/", "技术成长/数据与中间件/MySQL/"),
    ("04-Redis/", "技术成长/数据与中间件/Redis/"),
    ("05-Message-Queue/", "技术成长/数据与中间件/消息队列/"),
    ("18-AI-Engineering/", "技术成长/AI工程/"),
    ("01-Java/", "技术成长/Java/"),
    ("90-Growth/", "技术成长/00-通用/"),
    ("21-Interview/", "技术成长/00-通用/"),
    ("- 2026-07-01：从 `技术成长/数据与中间件/Redis/` 迁入。", ""),
    ("- 2026-07-01：MySQL 从 `技术成长/数据与中间件/MySQL/` 迁入。", ""),
]


def main() -> None:
    n = 0
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        t = md.read_text(encoding="utf-8")
        u = t
        for a, b in REPLACEMENTS:
            u = u.replace(a, b)
        if u != t:
            md.write_text(u, encoding="utf-8")
            n += 1
    print(f"Fixed {n} files.")


if __name__ == "__main__":
    main()
