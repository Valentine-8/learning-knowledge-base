# -*- coding: utf-8 -*-
"""Migrate repository to Repository-Specification structure."""
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"d:\学习")
os.chdir(ROOT)


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
    r = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True)
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
    dirs = [
        "00-Governance/03-Learning-Roadmaps",
        "01-Java/02-面向对象", "01-Java/03-集合框架", "01-Java/06-注解与反射",
        "01-Java/07-IO与NIO", "01-Java/08-Lambda与Stream",
        "02-Spring-Ecosystem/01-Spring-Framework",
        "03-Database/01-数据库基础", "03-Database/02-MySQL",
        "04-Redis", "05-Message-Queue", "06-Middleware/01-Elasticsearch",
        "08-JVM/01-JVM基础", "09-Concurrency/01-并发基础",
        "10-Distributed-Systems/01-分布式基础", "11-Architecture/01-架构基础",
        "15-DevOps/01-Git与协作",
        "16-Computer-Science/01-算法与数据结构", "16-Computer-Science/02-计算机网络",
        "16-Computer-Science/03-操作系统", "16-Computer-Science/04-安全",
        "18-AI-Engineering", "19-Cpp/01-语言与嵌入式", "19-Cpp/02-笔记",
        "21-Interview/01-面试方法论", "21-Interview/02-Java面试",
        "21-Interview/04-架构面试", "21-Interview/05-项目面试", "21-Interview/06-简历与求职",
        "90-Growth/01-学习方法", "90-Growth/02-工程素养", "90-Growth/03-职业发展",
        "90-Growth/04-个人模板",
        "98-Personal-Topics/Photography",
        "99-Archive/Frontend-Demos/Vue2-Basic", "99-Archive/Old-Roadmaps",
        "99-Archive/Legacy-Technical-Growth",
        "assets/images", "assets/diagrams", "assets/screenshots", "assets/examples",
        "07-Microservices", "12-Linux", "13-Docker", "14-Kubernetes",
        "17-Frontend", "20-Project-Practice",
    ]
    for d in dirs:
        ensure_dir(ROOT / d)

    move_files(ROOT / "技术成长/02-数据与中间件/01-MySQL", ROOT / "03-Database/02-MySQL")
    move_files(ROOT / "技术成长/02-数据与中间件/03-Redis", ROOT / "04-Redis")
    move_files(ROOT / "技术成长/02-数据与中间件/04-消息队列", ROOT / "05-Message-Queue")
    move_files(ROOT / "技术成长/02-数据与中间件/05-Elasticsearch", ROOT / "06-Middleware/01-Elasticsearch")

    move_files(ROOT / "技术成长/04-计算机基础/01-算法与数据结构", ROOT / "16-Computer-Science/01-算法与数据结构")
    move_files(ROOT / "技术成长/04-计算机基础/02-计算机网络", ROOT / "16-Computer-Science/02-计算机网络")
    move_files(ROOT / "技术成长/04-计算机基础/03-操作系统", ROOT / "16-Computer-Science/03-操作系统")
    move_files(ROOT / "技术成长/04-计算机基础/04-安全", ROOT / "16-Computer-Science/04-安全")

    move_files(ROOT / "技术成长/AI工程", ROOT / "18-AI-Engineering")
    move_files(ROOT / "技术成长/01-Java/笔记/phase1-集合", ROOT / "01-Java/03-集合框架")

    java_io = ROOT / "技术成长/01-Java/笔记/Java语言与IO"
    mappings = [
        (java_io / "01-面向对象与泛型.md", ROOT / "01-Java/02-面向对象/01-面向对象与泛型.md"),
        (java_io / "02-注解反射与异常.md", ROOT / "01-Java/06-注解与反射/02-注解反射与异常.md"),
        (java_io / "03-BIO-NIO与Netty.md", ROOT / "01-Java/07-IO与NIO/03-BIO-NIO与Netty.md"),
        (java_io / "04-Stream与新特性.md", ROOT / "01-Java/08-Lambda与Stream/04-Stream与新特性.md"),
        (java_io / "05-面试题库与案例.md", ROOT / "01-Java/02-面向对象/05-Java语言面试题库.md"),
        (java_io / "README.md", ROOT / "01-Java/07-IO与NIO/README-Java语言与IO.md"),
    ]
    for src, dst in mappings:
        git_mv(src, dst)

    phase_moves = [
        ("技术成长/01-Java/笔记/phase2-JVM/00-00-复习手册.md", "08-JVM/01-JVM基础/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase2-JVM/README.md", "08-JVM/01-JVM基础/README-phase2.md"),
        ("技术成长/01-Java/笔记/phase3-并发/00-00-复习手册.md", "09-Concurrency/01-并发基础/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase3-并发/README.md", "09-Concurrency/01-并发基础/README-phase3.md"),
        ("技术成长/01-Java/笔记/phase4-Spring/00-00-复习手册.md", "02-Spring-Ecosystem/01-Spring-Framework/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase4-Spring/README.md", "02-Spring-Ecosystem/01-Spring-Framework/README-phase4.md"),
        ("技术成长/01-Java/笔记/phase5-数据库/00-00-复习手册.md", "03-Database/01-数据库基础/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase5-数据库/README.md", "03-Database/01-数据库基础/README-phase5.md"),
        ("技术成长/01-Java/笔记/phase6-分布式/00-00-复习手册.md", "10-Distributed-Systems/01-分布式基础/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase6-分布式/README.md", "10-Distributed-Systems/01-分布式基础/README-phase6.md"),
        ("技术成长/01-Java/笔记/phase7-架构/00-00-复习手册.md", "11-Architecture/01-架构基础/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase7-架构/README.md", "11-Architecture/01-架构基础/README-phase7.md"),
        ("技术成长/01-Java/笔记/phase8-DevOps/00-00-复习手册.md", "15-DevOps/01-Git与协作/00-复习手册汇总.md"),
        ("技术成长/01-Java/笔记/phase8-DevOps/README.md", "15-DevOps/01-Git与协作/README-phase8.md"),
    ]
    for src, dst in phase_moves:
        git_mv(ROOT / src, ROOT / dst)

    meta_moves = [
        ("技术成长/01-Java/00-导航与面试/02-7年工程师技能全景索引.md", "00-Governance/03-Learning-Roadmaps/07-技能全景索引.md"),
        ("技术成长/01-Java/00-导航与面试/01-7年Java工程师技能清单.md", "00-Governance/03-Learning-Roadmaps/08-技能清单.md"),
        ("技术成长/01-Java/00-导航与面试/03-7年Java工程师学习路线.md", "00-Governance/03-Learning-Roadmaps/01-Java-Backend-Roadmap.md"),
        ("技术成长/01-Java/00-导航与面试/04-java学习.md", "01-Java/00-学习导航.md"),
        ("技术成长/01-Java/00-导航与面试/06-项目经历面试手册.md", "21-Interview/05-项目面试/01-06-项目经历面试手册.md"),
        ("技术成长/01-Java/00-导航与面试/07-面试题大全Q&A.md", "21-Interview/02-Java面试/06-07-面试题大全Q&A.md"),
        ("技术成长/01-Java/00-导航与面试/08-面试前速查.md", "21-Interview/02-Java面试/07-08-面试前速查.md"),
        ("技术成长/01-Java/00-导航与面试/09-系统设计练手.md", "21-Interview/04-架构面试/05-09-系统设计练手.md"),
        ("技术成长/01-Java/00-导航与面试/05-简历.md", "21-Interview/06-简历与求职/06-简历-Java.md"),
        ("技术成长/01-扩展技能全景.md", "00-Governance/03-Learning-Roadmaps/09-01-扩展技能全景.md"),
    ]
    for src, dst in meta_moves:
        git_mv(ROOT / src, ROOT / dst)

    cpp_dir = ROOT / "技术成长/C++嵌入式"
    if cpp_dir.is_dir():
        for f in list(cpp_dir.iterdir()):
            if f.name == "notes" and f.is_dir():
                git_mv(f, ROOT / "19-Cpp/02-笔记")
            elif f.is_file():
                keywords = ("简历", "面试", "公司", "岗位")
                if any(k in f.name for k in keywords):
                    git_mv(f, ROOT / "21-Interview/06-简历与求职" / f.name)
                else:
                    git_mv(f, ROOT / "19-Cpp/01-语言与嵌入式" / f.name)

    growth_moves = [
        ("技术成长/00-通用/11-11-工程素养-00-复习手册.md", "90-Growth/02-工程素养/01-工程素养00-复习手册.md"),
        ("技术成长/00-通用/01-01-阅读指南.md", "90-Growth/01-学习方法/01-阅读指南.md"),
        ("技术成长/00-通用/03-03-学习进度追踪.md", "90-Growth/01-学习方法/06-03-学习进度追踪.md"),
        ("技术成长/00-通用/04-04-个人基线评估.md", "90-Growth/01-学习方法/07-04-个人基线评估.md"),
        ("技术成长/00-通用/02-02-统一主路线.md", "90-Growth/01-学习方法/08-02-统一主路线.md"),
        ("技术成长/00-通用/05-05-错题与易忘概念.md", "90-Growth/01-学习方法/09-05-错题与易忘概念.md"),
        ("技术成长/00-通用/06-06-算法刷题记录.md", "90-Growth/01-学习方法/10-06-算法刷题记录.md"),
        ("技术成长/00-通用/07-07-Cursor操作手册.md", "90-Growth/01-学习方法/11-07-Cursor操作手册.md"),
        ("技术成长/00-通用/12-12-项目实战清单.md", "90-Growth/03-职业发展/06-12-项目实战清单.md"),
        ("技术成长/00-通用/13-13-周复盘模板.md", "90-Growth/04-个人模板/01-13-周复盘模板.md"),
        ("技术成长/00-通用/08-08-资源书签.md", "90-Growth/01-学习方法/12-08-资源书签.md"),
        ("技术成长/00-通用/09-09-求职追踪.md", "21-Interview/06-简历与求职/04-09-求职追踪.md"),
        ("技术成长/00-通用/10-10-面试与晋升素材库.md", "21-Interview/01-面试方法论/06-10-面试与晋升素材库.md"),
    ]
    for src, dst in growth_moves:
        git_mv(ROOT / src, ROOT / dst)

    move_files(ROOT / "技术成长/00-通用/archive", ROOT / "99-Archive/Old-Roadmaps")
    git_mv(ROOT / "技术成长/00-通用/reviews", ROOT / "90-Growth/05-周复盘记录")

    git_mv(ROOT / "奥林巴斯ep7/EP7-Guide", ROOT / "98-Personal-Topics/Photography/Olympus-EP7")
    git_mv(ROOT / "奥林巴斯ep7/.vscode", ROOT / "98-Personal-Topics/Photography/.vscode")
    git_mv(ROOT / "奥林巴斯ep7/md-preview-light.css", ROOT / "98-Personal-Topics/Photography/md-preview-light.css")

    vue_src = ROOT / "前端/vue"
    vue_dst = ROOT / "99-Archive/Frontend-Demos/Vue2-Basic"
    if vue_src.is_dir():
        for item in list(vue_src.iterdir()):
            git_mv(item, vue_dst / item.name)

    git_mv(ROOT / "技术成长", ROOT / "99-Archive/Legacy-Technical-Growth/技术成长")

    for spec, gov in [
        ("Repository-Specification.md", "00-Governance/01-Repository-Specification.md"),
        ("Repository-Structure.md", "00-Governance/02-Repository-Structure.md"),
    ]:
        src, dst = ROOT / spec, ROOT / gov
        if src.exists():
            shutil.copy2(src, dst)

    # cleanup empty legacy dirs
    for legacy in [ROOT / "前端", ROOT / "奥林巴斯ep7"]:
        if legacy.exists() and not any(legacy.iterdir()):
            legacy.rmdir()

    print("Migration complete.")


if __name__ == "__main__":
    main()
