# -*- coding: utf-8 -*-
"""Restore Chinese 技术成长 directory structure."""
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"d:\学习")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def git_mv(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    ensure_dir(dst.parent)
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    r = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        shutil.move(str(src), str(dst))


def move_files(src_dir: Path, dst_dir: Path) -> None:
    if not src_dir.is_dir():
        return
    ensure_dir(dst_dir)
    for f in list(src_dir.iterdir()):
        if f.is_file():
            git_mv(f, dst_dir / f.name)


def main() -> None:
    tg = ROOT / "技术成长"

    # --- 数据与中间件 ---
    move_files(ROOT / "03-Database/02-MySQL", tg / "数据与中间件/MySQL")
    move_files(ROOT / "04-Redis", tg / "数据与中间件/Redis")
    move_files(ROOT / "05-Message-Queue", tg / "数据与中间件/消息队列")
    move_files(ROOT / "06-Middleware/01-Elasticsearch", tg / "数据与中间件/Elasticsearch")

    # --- 计算机基础 ---
    move_files(ROOT / "16-Computer-Science/01-算法与数据结构", tg / "计算机基础/算法与数据结构")
    move_files(ROOT / "16-Computer-Science/02-计算机网络", tg / "计算机基础/计算机网络")
    move_files(ROOT / "16-Computer-Science/03-操作系统", tg / "计算机基础/操作系统")
    move_files(ROOT / "16-Computer-Science/04-安全", tg / "计算机基础/安全")

    # --- AI 工程 ---
    move_files(ROOT / "18-AI-Engineering", tg / "AI工程")

    # --- Java 集合 ---
    move_files(ROOT / "01-Java/03-集合框架", tg / "Java/笔记/phase1-集合")

    # --- Java 语言与 IO ---
    io = tg / "Java/笔记/Java语言与IO"
    ensure_dir(io)
    io_map = [
        (ROOT / "01-Java/02-面向对象/01-面向对象与泛型.md", io / "01-面向对象与泛型.md"),
        (ROOT / "01-Java/06-注解与反射/02-注解反射与异常.md", io / "02-注解反射与异常.md"),
        (ROOT / "01-Java/07-IO与NIO/03-BIO-NIO与Netty.md", io / "03-BIO-NIO与Netty.md"),
        (ROOT / "01-Java/08-Lambda与Stream/04-Stream与新特性.md", io / "04-Stream与新特性.md"),
        (ROOT / "01-Java/02-面向对象/05-Java语言面试题库.md", io / "05-面试题库与案例.md"),
        (ROOT / "01-Java/07-IO与NIO/README-Java语言与IO.md", io / "README.md"),
    ]
    for s, d in io_map:
        git_mv(s, d)

    # --- Java phase 复习手册 ---
    phases = [
        ("08-JVM/01-JVM基础", "phase2-JVM"),
        ("09-Concurrency/01-并发基础", "phase3-并发"),
        ("02-Spring-Ecosystem/01-Spring-Framework", "phase4-Spring"),
        ("03-Database/01-数据库基础", "phase5-数据库"),
        ("10-Distributed-Systems/01-分布式基础", "phase6-分布式"),
        ("11-Architecture/01-架构基础", "phase7-架构"),
        ("15-DevOps/01-Git与协作", "phase8-DevOps"),
    ]
    for src_sub, phase in phases:
        src = ROOT / src_sub
        dst = tg / f"Java/笔记/{phase}"
        ensure_dir(dst)
        git_mv(src / "00-复习手册汇总.md", dst / "复习手册.md")
        readme = list(src.glob("README-phase*.md"))
        if readme:
            git_mv(readme[0], dst / "README.md")

    # --- Java 元文档 ---
    meta = [
        ("01-Java/00-学习导航.md", "Java/java学习.md"),
        ("00-Governance/03-Learning-Roadmaps/07-技能全景索引.md", "Java/7年工程师技能全景索引.md"),
        ("00-Governance/03-Learning-Roadmaps/08-技能清单.md", "Java/7年Java工程师技能清单.md"),
        ("00-Governance/03-Learning-Roadmaps/01-Java-Backend-Roadmap.md", "Java/7年Java工程师学习路线.md"),
        ("00-Governance/03-Learning-Roadmaps/09-扩展技能全景.md", "扩展技能全景.md"),
        ("21-Interview/05-项目面试/01-项目经历面试手册.md", "Java/项目经历面试手册.md"),
        ("21-Interview/02-Java面试/06-面试题大全Q&A.md", "Java/面试题大全Q&A.md"),
        ("21-Interview/02-Java面试/07-面试前速查.md", "Java/面试前速查.md"),
        ("21-Interview/04-架构面试/05-系统设计练手.md", "Java/系统设计练手.md"),
        ("21-Interview/06-简历与求职/06-简历-Java.md", "Java/简历.md"),
    ]
    for s, d in meta:
        git_mv(ROOT / s, tg / d)

    # --- C++ ---
    cpp = tg / "C++嵌入式"
    ensure_dir(cpp)
    move_files(ROOT / "19-Cpp/01-语言与嵌入式", cpp)
    git_mv(ROOT / "19-Cpp/02-笔记", cpp / "notes")
    for f in ["简历-C++嵌入式.md", "面试前速查-C++嵌入式.md", "面试题大全-C++专题.md", "公司与岗位准备-广东宏大.md"]:
        git_mv(ROOT / "21-Interview/06-简历与求职" / f, cpp / f)

    # --- 00-通用（恢复原名，去掉编号前缀）---
    common = tg / "00-通用"
    ensure_dir(common)
    growth_map = [
        ("90-Growth/02-工程素养/01-工程素养复习手册.md", "工程素养-复习手册.md"),
        ("90-Growth/01-学习方法/00-阅读指南.md", "阅读指南.md"),
        ("90-Growth/01-学习方法/06-学习进度追踪.md", "学习进度追踪.md"),
        ("90-Growth/01-学习方法/07-个人基线评估.md", "个人基线评估.md"),
        ("90-Growth/01-学习方法/08-统一主路线.md", "统一主路线.md"),
        ("90-Growth/01-学习方法/09-错题与易忘概念.md", "错题与易忘概念.md"),
        ("90-Growth/01-学习方法/10-算法刷题记录.md", "算法刷题记录.md"),
        ("90-Growth/01-学习方法/11-Cursor操作手册.md", "Cursor操作手册.md"),
        ("90-Growth/01-学习方法/12-资源书签.md", "资源书签.md"),
        ("90-Growth/03-职业发展/06-项目实战清单.md", "项目实战清单.md"),
        ("90-Growth/04-个人模板/01-周复盘模板.md", "周复盘模板.md"),
        ("21-Interview/06-简历与求职/04-求职追踪.md", "求职追踪.md"),
        ("21-Interview/01-面试方法论/06-面试与晋升素材库.md", "面试与晋升素材库.md"),
    ]
    for s, d in growth_map:
        git_mv(ROOT / s, common / d)

    ensure_dir(common / "archive")
    move_files(ROOT / "99-Archive/Old-Roadmaps", common / "archive")
    git_mv(ROOT / "90-Growth/05-周复盘记录", common / "reviews")

    # --- 摄影 & 前端 ---
    git_mv(ROOT / "98-Personal-Topics/Photography/Olympus-EP7", ROOT / "奥林巴斯ep7/EP7-Guide")
    if (ROOT / "98-Personal-Topics/Photography/.vscode").exists():
        git_mv(ROOT / "98-Personal-Topics/Photography/.vscode", ROOT / "奥林巴斯ep7/.vscode")
    if (ROOT / "98-Personal-Topics/Photography/md-preview-light.css").exists():
        git_mv(ROOT / "98-Personal-Topics/Photography/md-preview-light.css", ROOT / "奥林巴斯ep7/md-preview-light.css")

    vue_dst = ROOT / "前端/vue"
    ensure_dir(vue_dst)
    move_files(ROOT / "99-Archive/Frontend-Demos/Vue2-Basic", vue_dst)

    # --- 恢复技术成长 README（从归档副本）---
    legacy_readme = ROOT / "99-Archive/Legacy-Technical-Growth/技术成长/README.md"
    if legacy_readme.exists():
        ensure_dir(tg)
        shutil.copy2(legacy_readme, tg / "README.md")

    # --- 规范文档改为中文目录名 ---
    gov_cn = ROOT / "规范文档"
    ensure_dir(gov_cn)
    for name in ["Repository-Specification.md", "Repository-Structure.md"]:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, gov_cn / name)
    mig = ROOT / "00-Governance/06-Migration-Guide.md"
    if mig.exists():
        shutil.copy2(mig, gov_cn / "迁移说明-2026-07.md")

    # --- 删除空的英文顶层目录 ---
    english_tops = [
        "00-Governance", "01-Java", "02-Spring-Ecosystem", "03-Database", "04-Redis",
        "05-Message-Queue", "06-Middleware", "07-Microservices", "08-JVM", "09-Concurrency",
        "10-Distributed-Systems", "11-Architecture", "12-Linux", "13-Docker", "14-Kubernetes",
        "15-DevOps", "16-Computer-Science", "17-Frontend", "18-AI-Engineering", "19-Cpp",
        "20-Project-Practice", "21-Interview", "90-Growth", "98-Personal-Topics", "assets",
    ]
    for d in english_tops:
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

    # 清理归档里的重复空壳
    legacy = ROOT / "99-Archive/Legacy-Technical-Growth"
    if legacy.exists():
        shutil.rmtree(legacy, ignore_errors=True)
    archive = ROOT / "99-Archive"
    if archive.exists() and not any(archive.iterdir()):
        archive.rmdir()

    print("Restore complete.")


if __name__ == "__main__":
    main()
