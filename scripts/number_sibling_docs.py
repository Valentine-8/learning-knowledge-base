# -*- coding: utf-8 -*-
"""Add numeric prefixes to peer-level docs/folders and fix markdown links."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"d:\学习")
SKIP_DIRS = {".git", "node_modules", "99-Archive", "archive", "reviews", "notes"}

# (old_relative, new_relative) — paths use forward slashes for keys
RENAMES: list[tuple[str, str]] = [
    # 技术成长 root
    ("技术成长/01-扩展技能全景.md", "技术成长/01-扩展技能全景.md"),
    # 00-通用
    ("技术成长/00-通用/01-01-阅读指南.md", "技术成长/00-通用/01-01-阅读指南.md"),
    ("技术成长/00-通用/02-02-统一主路线.md", "技术成长/00-通用/02-02-统一主路线.md"),
    ("技术成长/00-通用/03-03-学习进度追踪.md", "技术成长/00-通用/03-03-学习进度追踪.md"),
    ("技术成长/00-通用/04-04-个人基线评估.md", "技术成长/00-通用/04-04-个人基线评估.md"),
    ("技术成长/00-通用/05-05-错题与易忘概念.md", "技术成长/00-通用/05-05-错题与易忘概念.md"),
    ("技术成长/00-通用/06-06-算法刷题记录.md", "技术成长/00-通用/06-06-算法刷题记录.md"),
    ("技术成长/00-通用/07-07-Cursor操作手册.md", "技术成长/00-通用/07-07-Cursor操作手册.md"),
    ("技术成长/00-通用/08-08-资源书签.md", "技术成长/00-通用/08-08-资源书签.md"),
    ("技术成长/00-通用/09-09-求职追踪.md", "技术成长/00-通用/09-09-求职追踪.md"),
    ("技术成长/00-通用/10-10-面试与晋升素材库.md", "技术成长/00-通用/10-10-面试与晋升素材库.md"),
    ("技术成长/00-通用/11-11-工程素养-00-复习手册.md", "技术成长/00-通用/11-11-工程素养-00-复习手册.md"),
    ("技术成长/00-通用/12-12-项目实战清单.md", "技术成长/00-通用/12-12-项目实战清单.md"),
    ("技术成长/00-通用/13-13-周复盘模板.md", "技术成长/00-通用/13-13-周复盘模板.md"),
    # Java root files
    ("技术成长/01-Java/01-7年Java工程师技能清单.md", "技术成长/01-Java/01-7年Java工程师技能清单.md"),
    ("技术成长/01-Java/02-7年工程师技能全景索引.md", "技术成长/01-Java/02-7年工程师技能全景索引.md"),
    ("技术成长/01-Java/03-7年Java工程师学习路线.md", "技术成长/01-Java/03-7年Java工程师学习路线.md"),
    ("技术成长/01-Java/04-java学习.md", "技术成长/01-Java/04-java学习.md"),
    ("技术成长/01-Java/05-简历.md", "技术成长/01-Java/05-简历.md"),
    ("技术成长/01-Java/06-项目经历面试手册.md", "技术成长/01-Java/06-项目经历面试手册.md"),
    ("技术成长/01-Java/07-面试题大全Q&A.md", "技术成长/01-Java/07-面试题大全Q&A.md"),
    ("技术成长/01-Java/08-面试前速查.md", "技术成长/01-Java/08-面试前速查.md"),
    ("技术成长/01-Java/09-系统设计练手.md", "技术成长/01-Java/09-系统设计练手.md"),
    # Java topic folders
    ("技术成长/01-Java/01-集合", "技术成长/01-Java/01-集合"),
    ("技术成长/01-Java/02-JVM", "技术成长/01-Java/02-JVM"),
    ("技术成长/01-Java/03-并发", "技术成长/01-Java/03-并发"),
    ("技术成长/01-Java/04-Spring", "技术成长/01-Java/04-Spring"),
    ("技术成长/01-Java/05-SpringCloud", "技术成长/01-Java/05-SpringCloud"),
    ("技术成长/01-Java/06-JPA", "技术成长/01-Java/06-JPA"),
    ("技术成长/01-Java/07-WebFlux", "技术成长/01-Java/07-WebFlux"),
    ("技术成长/01-Java/08-分布式", "技术成长/01-Java/08-分布式"),
    ("技术成长/01-Java/09-架构", "技术成长/01-Java/09-架构"),
    ("技术成长/01-Java/10-Maven与Gradle", "技术成长/01-Java/10-Maven与Gradle"),
    ("技术成长/01-Java/11-测试", "技术成长/01-Java/11-测试"),
    ("技术成长/01-Java/12-压测", "技术成长/01-Java/12-压测"),
    # Java 笔记 phase 复习手册 + phase1 notes
    ("技术成长/01-Java/笔记/phase1-集合/00-00-复习手册.md", "技术成长/01-Java/笔记/phase1-集合/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase2-JVM/00-00-复习手册.md", "技术成长/01-Java/笔记/phase2-JVM/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase3-并发/00-00-复习手册.md", "技术成长/01-Java/笔记/phase3-并发/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase4-Spring/00-00-复习手册.md", "技术成长/01-Java/笔记/phase4-Spring/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase5-数据库/00-00-复习手册.md", "技术成长/01-Java/笔记/phase5-数据库/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase6-分布式/00-00-复习手册.md", "技术成长/01-Java/笔记/phase6-分布式/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase7-架构/00-00-复习手册.md", "技术成长/01-Java/笔记/phase7-架构/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase8-DevOps/00-00-复习手册.md", "技术成长/01-Java/笔记/phase8-DevOps/00-00-复习手册.md"),
    ("技术成长/01-Java/笔记/phase1-集合/01-01-ArrayList.md", "技术成长/01-Java/笔记/phase1-集合/01-01-ArrayList.md"),
    ("技术成长/01-Java/笔记/phase1-集合/02-02-HashMap.md", "技术成长/01-Java/笔记/phase1-集合/02-02-HashMap.md"),
    ("技术成长/01-Java/笔记/phase1-集合/03-ConcurrentHashMap.md", "技术成长/01-Java/笔记/phase1-集合/03-ConcurrentHashMap.md"),
    # 数据与中间件 folders
    ("技术成长/02-数据与中间件/01-MySQL", "技术成长/02-数据与中间件/01-MySQL"),
    ("技术成长/02-数据与中间件/02-PostgreSQL", "技术成长/02-数据与中间件/02-PostgreSQL"),
    ("技术成长/02-数据与中间件/03-Redis", "技术成长/02-数据与中间件/03-Redis"),
    ("技术成长/02-数据与中间件/04-消息队列", "技术成长/02-数据与中间件/04-消息队列"),
    ("技术成长/02-数据与中间件/05-Elasticsearch", "技术成长/02-数据与中间件/05-Elasticsearch"),
    ("技术成长/02-数据与中间件/06-MongoDB", "技术成长/02-数据与中间件/06-MongoDB"),
    ("技术成长/02-数据与中间件/07-gRPC", "技术成长/02-数据与中间件/07-gRPC"),
    ("技术成长/02-数据与中间件/08-ZooKeeper", "技术成长/02-数据与中间件/08-ZooKeeper"),
    ("技术成长/02-数据与中间件/09-大数据", "技术成长/02-数据与中间件/09-大数据"),
    # 运维与部署 folders
    ("技术成长/03-运维与部署/01-Linux", "技术成长/03-运维与部署/01-Linux"),
    ("技术成长/03-运维与部署/02-Shell", "技术成长/03-运维与部署/02-Shell"),
    ("技术成长/03-运维与部署/03-Git", "技术成长/03-运维与部署/03-Git"),
    ("技术成长/03-运维与部署/04-Nginx", "技术成长/03-运维与部署/04-Nginx"),
    ("技术成长/03-运维与部署/05-Docker", "技术成长/03-运维与部署/05-Docker"),
    ("技术成长/03-运维与部署/06-Kubernetes", "技术成长/03-运维与部署/06-Kubernetes"),
    ("技术成长/03-运维与部署/07-CI-CD", "技术成长/03-运维与部署/07-CI-CD"),
    ("技术成长/03-运维与部署/08-可观测性", "技术成长/03-运维与部署/08-可观测性"),
    ("技术成长/03-运维与部署/09-云平台", "技术成长/03-运维与部署/09-云平台"),
    # 计算机基础 folders
    ("技术成长/04-计算机基础/01-算法与数据结构", "技术成长/04-计算机基础/01-算法与数据结构"),
    ("技术成长/04-计算机基础/02-计算机网络", "技术成长/04-计算机基础/02-计算机网络"),
    ("技术成长/04-计算机基础/03-操作系统", "技术成长/04-计算机基础/03-操作系统"),
    ("技术成长/04-计算机基础/04-安全", "技术成长/04-计算机基础/04-安全"),
    # 扩展语言 folders
    ("技术成长/07-扩展语言/01-Python", "技术成长/07-扩展语言/01-Python"),
    ("技术成长/07-扩展语言/02-Go", "技术成长/07-扩展语言/02-Go"),
    # Python extras (before folder rename to 01-Python)
    ("技术成长/07-扩展语言/01-Python/16-00-复习手册.md", "技术成长/07-扩展语言/01-Python/16-00-复习手册.md"),
    ("技术成长/07-扩展语言/01-Python/99-99-附录-Java与Python对照.md", "技术成长/07-扩展语言/01-Python/99-99-附录-Java与Python对照.md"),
    # AI 工程 supplements
    ("技术成长/05-AI工程/00-00-AI时代开发者技能与概念手册.md", "技术成长/05-AI工程/00-00-AI时代开发者技能与概念手册.md"),
    ("技术成长/05-AI工程/13-13-AI时代程序员与代码.md", "技术成长/05-AI工程/13-13-AI时代程序员与代码.md"),
    ("技术成长/05-AI工程/14-14-面试题大全-AI专题.md", "技术成长/05-AI工程/14-14-面试题大全-AI专题.md"),
    # C++ 嵌入式
    ("技术成长/06-C++嵌入式/01-01-公司与岗位准备-广东宏大.md", "技术成长/06-C++嵌入式/01-01-公司与岗位准备-广东宏大.md"),
    ("技术成长/06-C++嵌入式/02-02-C++嵌入式复习路线.md", "技术成长/06-C++嵌入式/02-02-C++嵌入式复习路线.md"),
    ("技术成长/06-C++嵌入式/03-03-复习进度追踪.md", "技术成长/06-C++嵌入式/03-03-复习进度追踪.md"),
    ("技术成长/06-C++嵌入式/04-04-从Java到C++嵌入式-迁移指南.md", "技术成长/06-C++嵌入式/04-04-从Java到C++嵌入式-迁移指南.md"),
    ("技术成长/06-C++嵌入式/05-05-嵌入式八股速查.md", "技术成长/06-C++嵌入式/05-05-嵌入式八股速查.md"),
    ("技术成长/06-C++嵌入式/06-06-手写代码题集.md", "技术成长/06-C++嵌入式/06-06-手写代码题集.md"),
    ("技术成长/06-C++嵌入式/07-07-简历-C++嵌入式.md", "技术成长/06-C++嵌入式/07-07-简历-C++嵌入式.md"),
    ("技术成长/06-C++嵌入式/08-面试前速查-C++嵌入式.md", "技术成长/06-C++嵌入式/08-面试前速查-C++嵌入式.md"),
    ("技术成长/06-C++嵌入式/09-09-面试题大全-C++专题.md", "技术成长/06-C++嵌入式/09-09-面试题大全-C++专题.md"),
]


def to_path(rel: str) -> Path:
    return ROOT / rel.replace("/", "\\")


def git_mv(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"SKIP missing: {src}")
        return
    if dst.exists():
        print(f"SKIP exists: {dst}")
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
        print(f"move (non-git): {src.name} -> {dst.name}")
    else:
        print(f"git mv: {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")


def apply_renames() -> None:
    # Longest paths first to avoid nested conflicts
    ordered = sorted(RENAMES, key=lambda x: len(x[0]), reverse=True)
    for old_rel, new_rel in ordered:
        git_mv(to_path(old_rel), to_path(new_rel))


def build_replacements() -> list[tuple[str, str]]:
    reps: list[tuple[str, str]] = []
    for old_rel, new_rel in RENAMES:
        old_posix = old_rel.replace("\\", "/")
        new_posix = new_rel.replace("\\", "/")
        reps.append((old_posix, new_posix))
        if not old_rel.endswith(".md"):
            reps.append((old_posix + "/", new_posix + "/"))
        old_name = Path(old_rel).name
        new_name = Path(new_rel).name
        if old_name != new_name and old_name.endswith(".md"):
            # basename-only replacements break nested names (e.g. 01-List与ArrayList)
            pass
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for old, new in sorted(reps, key=lambda x: len(x[0]), reverse=True):
        if old not in seen:
            seen.add(old)
            unique.append((old, new))
    return unique


def fix_links(replacements: list[tuple[str, str]]) -> int:
    changed_files = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".json", ".py", ".ps1", ".html", ".css"}:
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
            changed_files += 1
            print(f"updated links: {path.relative_to(ROOT)}")
    return changed_files


def main() -> None:
    apply_renames()
    reps = build_replacements()
    n = fix_links(reps)
    print(f"\nDone. Updated {n} files with new link paths.")


if __name__ == "__main__":
    main()
