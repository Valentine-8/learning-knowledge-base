# -*- coding: utf-8 -*-
"""Move 01-Java root nav/interview docs into 00-导航与面试/ and fix links."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"d:\学习")
JAVA = ROOT / "技术成长" / "01-Java"
TARGET = JAVA / "00-导航与面试"

FILES = [
    "01-7年Java工程师技能清单.md",
    "02-7年工程师技能全景索引.md",
    "03-7年Java工程师学习路线.md",
    "04-java学习.md",
    "05-简历.md",
    "06-项目经历面试手册.md",
    "07-面试题大全Q&A.md",
    "08-面试前速查.md",
    "09-系统设计练手.md",
]

PATH_REPLACEMENTS = [
    ("01-Java/00-导航与面试/09-系统设计练手.md", "01-Java/00-导航与面试/09-系统设计练手.md"),
    ("01-Java/00-导航与面试/08-面试前速查.md", "01-Java/00-导航与面试/08-面试前速查.md"),
    ("01-Java/00-导航与面试/07-面试题大全Q&A.md", "01-Java/00-导航与面试/07-面试题大全Q&A.md"),
    ("01-Java/00-导航与面试/06-项目经历面试手册.md", "01-Java/00-导航与面试/06-项目经历面试手册.md"),
    ("01-Java/00-导航与面试/05-简历.md", "01-Java/00-导航与面试/05-简历.md"),
    ("01-Java/00-导航与面试/04-java学习.md", "01-Java/00-导航与面试/04-java学习.md"),
    ("01-Java/00-导航与面试/03-7年Java工程师学习路线.md", "01-Java/00-导航与面试/03-7年Java工程师学习路线.md"),
    ("01-Java/00-导航与面试/02-7年工程师技能全景索引.md", "01-Java/00-导航与面试/02-7年工程师技能全景索引.md"),
    ("01-Java/00-导航与面试/01-7年Java工程师技能清单.md", "01-Java/00-导航与面试/01-7年Java工程师技能清单.md"),
]

# Inside moved files: one level deeper
MOVED_FILE_FIXES = [
    ("](../00-通用/", "](../../00-通用/"),
    ("](../01-扩展技能全景.md", "](../../01-扩展技能全景.md"),
    ("](../02-数据与中间件/", "](../../02-数据与中间件/"),
    ("](../03-运维与部署/", "](../../03-运维与部署/"),
    ("](../04-计算机基础/", "](../../04-计算机基础/"),
    ("](../05-AI工程/", "](../../05-AI工程/"),
    ("](../06-C++嵌入式/", "](../../06-C++嵌入式/"),
    ("](../07-扩展语言/", "](../../07-扩展语言/"),
    ("](../README.md)", "](../README.md)"),  # 01-Java README — unchanged
    ("](./01-集合/", "](../01-集合/"),
    ("](./02-JVM/", "](../02-JVM/"),
    ("](./03-并发/", "](../03-并发/"),
    ("](./04-Spring/", "](../04-Spring/"),
    ("](./05-SpringCloud/", "](../05-SpringCloud/"),
    ("](./06-JPA/", "](../06-JPA/"),
    ("](./07-WebFlux/", "](../07-WebFlux/"),
    ("](./08-分布式/", "](../08-分布式/"),
    ("](./09-架构/", "](../09-架构/"),
    ("](./10-Maven与Gradle/", "](../10-Maven与Gradle/"),
    ("](./11-测试/", "](../11-测试/"),
    ("](./12-压测/", "](../12-压测/"),
    ("](./笔记/", "](../笔记/"),
]


def git_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        shutil.move(str(src), str(dst))


def fix_moved_file(text: str) -> str:
    for old, new in MOVED_FILE_FIXES:
        text = text.replace(old, new)
    # skill index paths like ./01-集合/ already handled; ./笔记/ handled
    return text


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        src = JAVA / name
        dst = TARGET / name
        if src.exists():
            git_mv(src, dst)
            print(f"moved: {name}")

    # Fix moved files internal links
    for path in TARGET.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = fix_moved_file(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")

    # Fix repo-wide links
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".ps1", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        original = text
        for old, new in PATH_REPLACEMENTS:
            text = text.replace(old, new)
        if path.parent == TARGET and path.name in FILES:
            text = fix_moved_file(text)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
    print(f"updated {changed} files")


if __name__ == "__main__":
    main()
