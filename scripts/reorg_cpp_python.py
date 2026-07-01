# -*- coding: utf-8 -*-
"""Move C++ nav docs to 00-导航与面试/; Python intro docs to 00-入门/."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"d:\学习")

# --- C++ embedded ---
CPP = ROOT / "技术成长" / "06-C++嵌入式"
CPP_TARGET = CPP / "00-导航与面试"
CPP_FILES = [
    "01-公司与岗位准备-广东宏大.md",
    "02-C++嵌入式复习路线.md",
    "03-复习进度追踪.md",
    "04-从Java到C++嵌入式-迁移指南.md",
    "05-嵌入式八股速查.md",
    "06-手写代码题集.md",
    "07-简历-C++嵌入式.md",
    "08-面试前速查-C++嵌入式.md",
    "09-面试题大全-C++专题.md",
]

CPP_PATH_REPLACEMENTS = [
    ("06-C++嵌入式/00-导航与面试/01-公司与岗位准备-广东宏大.md", "06-C++嵌入式/00-导航与面试/01-公司与岗位准备-广东宏大.md"),
    ("06-C++嵌入式/00-导航与面试/02-C++嵌入式复习路线.md", "06-C++嵌入式/00-导航与面试/02-C++嵌入式复习路线.md"),
    ("06-C++嵌入式/00-导航与面试/03-复习进度追踪.md", "06-C++嵌入式/00-导航与面试/03-复习进度追踪.md"),
    ("06-C++嵌入式/00-导航与面试/04-从Java到C++嵌入式-迁移指南.md", "06-C++嵌入式/00-导航与面试/04-从Java到C++嵌入式-迁移指南.md"),
    ("06-C++嵌入式/00-导航与面试/05-嵌入式八股速查.md", "06-C++嵌入式/00-导航与面试/05-嵌入式八股速查.md"),
    ("06-C++嵌入式/00-导航与面试/06-手写代码题集.md", "06-C++嵌入式/00-导航与面试/06-手写代码题集.md"),
    ("06-C++嵌入式/00-导航与面试/07-简历-C++嵌入式.md", "06-C++嵌入式/00-导航与面试/07-简历-C++嵌入式.md"),
    ("06-C++嵌入式/00-导航与面试/08-面试前速查-C++嵌入式.md", "06-C++嵌入式/00-导航与面试/08-面试前速查-C++嵌入式.md"),
    ("06-C++嵌入式/00-导航与面试/09-面试题大全-C++专题.md", "06-C++嵌入式/00-导航与面试/09-面试题大全-C++专题.md"),
]

CPP_MOVED_FIXES = [
    ("](../00-通用/", "](../../00-通用/"),
    ("](../01-Java/", "](../../01-Java/"),
    ("](../README.md)", "](../../README.md)"),  # 技术成长 README
    ("](./README.md)", "](../README.md)"),  # 06-C++ 根 README
]

# --- Python intro ---
PY = ROOT / "技术成长" / "07-扩展语言" / "01-Python"
PY_TARGET = PY / "00-入门"
PY_MOVES = {
    "00-Java开发者学习指南.md": "01-Java开发者学习指南.md",
    "00-学习路线图.md": "02-学习路线图.md",
}

PY_PATH_REPLACEMENTS = [
    ("01-Python/00-入门/01-Java开发者学习指南.md", "01-Python/00-入门/01-Java开发者学习指南.md"),
    ("01-Python/00-入门/02-学习路线图.md", "01-Python/00-入门/02-学习路线图.md"),
    ("Python/00-入门/01-Java开发者学习指南", "Python/00-入门/01-Java开发者学习指南"),
]

PY_MOVED_FIXES = [
    ("](../../05-AI工程/", "](../../../05-AI工程/"),
    ("](../../02-数据与中间件/", "](../../../02-数据与中间件/"),
    ("](../../01-Java/", "](../../../01-Java/"),
    ("](../../01-扩展技能全景", "](../../../01-扩展技能全景"),
    ("](./99-附录", "](../99-附录"),
    ("](./00-速查总览", "](../00-速查总览"),
    ("](./README.md)", "](../README.md)"),
    ("](./00-学习路线图", "](./02-学习路线图"),
    ("](./00-Java开发者学习指南", "](./01-Java开发者学习指南"),
    ("](./01-安装", "](../01-安装"),
    ("](./02-变量", "](../02-变量"),
    ("](./03-字符串", "](../03-字符串"),
    ("](./04-列表", "](../04-列表"),
    ("](./05-字典", "](../05-字典"),
    ("](./06-流程", "](../06-流程"),
    ("](./07-函数", "](../07-函数"),
    ("](./08-文件", "](../08-文件"),
    ("](./09-模块", "](../09-模块"),
    ("](./10-面向", "](../10-面向"),
    ("](./11-进阶", "](../11-进阶"),
    ("](./12-常用", "](../12-常用"),
    ("](./13-HTTP", "](../13-HTTP"),
    ("](./14-并发", "](../14-并发"),
    ("](./15-综合", "](../15-综合"),
    ("](./16-复习", "](../16-复习"),
]

PY_CHAPTER_FIXES = [
    ("./00-Java开发者学习指南.md", "./00-入门/01-Java开发者学习指南.md"),
    ("./00-学习路线图.md", "./00-入门/02-学习路线图.md"),
]


def git_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        shutil.move(str(src), str(dst))


def apply_fixes(text: str, fixes: list[tuple[str, str]]) -> str:
    for old, new in fixes:
        text = text.replace(old, new)
    return text


def update_repo(replacements: list[tuple[str, str]]) -> int:
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
        for old, new in replacements:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def move_cpp() -> None:
    CPP_TARGET.mkdir(parents=True, exist_ok=True)
    for name in CPP_FILES:
        src = CPP / name
        dst = CPP_TARGET / name
        if src.exists():
            git_mv(src, dst)
            print(f"cpp moved: {name}")

    for path in CPP_TARGET.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = apply_fixes(text, CPP_MOVED_FIXES)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")

    n = update_repo(CPP_PATH_REPLACEMENTS)
    print(f"cpp link updates: {n} files")


def move_python() -> None:
    PY_TARGET.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in PY_MOVES.items():
        src = PY / src_name
        dst = PY_TARGET / dst_name
        if src.exists():
            git_mv(src, dst)
            print(f"python moved: {src_name} -> 00-入门/{dst_name}")

    for path in PY_TARGET.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = apply_fixes(text, PY_MOVED_FIXES)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")

    for path in PY.glob("*.md"):
        if path.parent != PY:
            continue
        text = path.read_text(encoding="utf-8")
        updated = apply_fixes(text, PY_CHAPTER_FIXES)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")

    # 99-附录 at PY root
    appendix = PY / "99-附录-Java与Python对照.md"
    if appendix.exists():
        text = appendix.read_text(encoding="utf-8")
        updated = apply_fixes(text, PY_CHAPTER_FIXES)
        if updated != text:
            appendix.write_text(updated, encoding="utf-8", newline="\n")

    n = update_repo(PY_PATH_REPLACEMENTS)
    print(f"python link updates: {n} files")


def main() -> None:
    move_cpp()
    move_python()


if __name__ == "__main__":
    main()
