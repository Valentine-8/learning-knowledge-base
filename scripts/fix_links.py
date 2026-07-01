# -*- coding: utf-8 -*-
"""Fix markdown links after repository restructure."""
import re
from pathlib import Path

ROOT = Path(r"d:\学习")
SKIP = ROOT / "99-Archive" / "Legacy-Technical-Growth"

REPLACEMENTS = [
    ("技术成长/02-数据与中间件/01-MySQL/", "03-Database/02-MySQL/"),
    ("技术成长/02-数据与中间件/03-Redis/", "04-Redis/"),
    ("技术成长/02-数据与中间件/04-消息队列/", "05-Message-Queue/"),
    ("技术成长/02-数据与中间件/05-Elasticsearch/", "06-Middleware/01-Elasticsearch/"),
    ("技术成长/02-数据与中间件/", "03-Database/"),
    ("技术成长/04-计算机基础/01-算法与数据结构/", "16-Computer-Science/01-算法与数据结构/"),
    ("技术成长/04-计算机基础/02-计算机网络/", "16-Computer-Science/02-计算机网络/"),
    ("技术成长/04-计算机基础/03-操作系统/", "16-Computer-Science/03-操作系统/"),
    ("技术成长/04-计算机基础/04-安全/", "16-Computer-Science/04-安全/"),
    ("技术成长/04-计算机基础/", "16-Computer-Science/"),
    ("技术成长/05-AI工程/", "18-AI-Engineering/"),
    ("技术成长/06-C++嵌入式/", "19-Cpp/01-语言与嵌入式/"),
    ("技术成长/01-Java/笔记/phase1-集合/", "01-Java/03-集合框架/"),
    ("技术成长/01-Java/笔记/Java语言与IO/", "01-Java/07-IO与NIO/"),
    ("技术成长/01-Java/笔记/phase2-JVM/", "08-JVM/01-JVM基础/"),
    ("技术成长/01-Java/笔记/phase3-并发/", "09-Concurrency/01-并发基础/"),
    ("技术成长/01-Java/笔记/phase4-Spring/", "02-Spring-Ecosystem/01-Spring-Framework/"),
    ("技术成长/01-Java/笔记/phase5-数据库/", "03-Database/01-数据库基础/"),
    ("技术成长/01-Java/笔记/phase6-分布式/", "10-Distributed-Systems/01-分布式基础/"),
    ("技术成长/01-Java/笔记/phase7-架构/", "11-Architecture/01-架构基础/"),
    ("技术成长/01-Java/笔记/phase8-DevOps/", "15-DevOps/01-Git与协作/"),
    ("技术成长/01-Java/02-7年工程师技能全景索引.md", "00-Governance/03-Learning-Roadmaps/07-技能全景索引.md"),
    ("技术成长/01-Java/01-7年Java工程师技能清单.md", "00-Governance/03-Learning-Roadmaps/08-技能清单.md"),
    ("技术成长/01-Java/03-7年Java工程师学习路线.md", "00-Governance/03-Learning-Roadmaps/01-Java-Backend-Roadmap.md"),
    ("技术成长/01-Java/04-java学习.md", "01-Java/00-学习导航.md"),
    ("技术成长/01-Java/06-项目经历面试手册.md", "21-Interview/05-项目面试/01-06-项目经历面试手册.md"),
    ("技术成长/01-Java/07-面试题大全Q&A.md", "21-Interview/02-Java面试/06-07-面试题大全Q&A.md"),
    ("技术成长/01-Java/08-面试前速查.md", "21-Interview/02-Java面试/07-08-面试前速查.md"),
    ("技术成长/01-Java/09-系统设计练手.md", "21-Interview/04-架构面试/05-09-系统设计练手.md"),
    ("技术成长/01-Java/05-简历.md", "21-Interview/06-简历与求职/06-简历-Java.md"),
    ("技术成长/01-Java/README.md", "01-Java/README.md"),
    ("技术成长/01-Java/", "01-Java/"),
    ("技术成长/00-通用/11-11-工程素养-00-复习手册.md", "90-Growth/02-工程素养/01-工程素养00-复习手册.md"),
    ("技术成长/00-通用/01-01-阅读指南.md", "90-Growth/01-学习方法/01-阅读指南.md"),
    ("技术成长/00-通用/03-03-学习进度追踪.md", "90-Growth/01-学习方法/06-03-学习进度追踪.md"),
    ("技术成长/00-通用/04-04-个人基线评估.md", "90-Growth/01-学习方法/07-04-个人基线评估.md"),
    ("技术成长/00-通用/02-02-统一主路线.md", "90-Growth/01-学习方法/08-02-统一主路线.md"),
    ("技术成长/00-通用/05-05-错题与易忘概念.md", "90-Growth/01-学习方法/09-05-错题与易忘概念.md"),
    ("技术成长/00-通用/06-06-算法刷题记录.md", "90-Growth/01-学习方法/10-06-算法刷题记录.md"),
    ("技术成长/00-通用/07-07-Cursor操作手册.md", "90-Growth/01-学习方法/11-07-Cursor操作手册.md"),
    ("技术成长/00-通用/13-13-周复盘模板.md", "90-Growth/04-个人模板/01-13-周复盘模板.md"),
    ("技术成长/00-通用/08-08-资源书签.md", "90-Growth/01-学习方法/12-08-资源书签.md"),
    ("技术成长/00-通用/09-09-求职追踪.md", "21-Interview/06-简历与求职/04-09-求职追踪.md"),
    ("技术成长/00-通用/10-10-面试与晋升素材库.md", "21-Interview/01-面试方法论/06-10-面试与晋升素材库.md"),
    ("技术成长/00-通用/", "90-Growth/01-学习方法/"),
    ("技术成长/01-扩展技能全景.md", "00-Governance/03-Learning-Roadmaps/09-01-扩展技能全景.md"),
    ("技术成长/README.md", "README.md"),
    ("技术成长/", ""),
    ("奥林巴斯ep7/EP7-Guide/", "98-Personal-Topics/Photography/Olympus-EP7/"),
    ("前端/vue/", "99-Archive/Frontend-Demos/Vue2-Basic/"),
    # same-folder renames in 90-Growth
    ("./02-统一主路线.md", "./08-02-统一主路线.md"),
    ("./03-学习进度追踪.md", "./06-03-学习进度追踪.md"),
    ("./04-个人基线评估.md", "./07-04-个人基线评估.md"),
    ("./05-错题与易忘概念.md", "./09-05-错题与易忘概念.md"),
    ("./06-算法刷题记录.md", "./10-06-算法刷题记录.md"),
    ("./13-周复盘模板.md", "../04-个人模板/01-13-周复盘模板.md"),
    ("./07-Cursor操作手册.md", "./11-07-Cursor操作手册.md"),
    ("./08-资源书签.md", "./12-08-资源书签.md"),
    ("./09-求职追踪.md", "../../21-Interview/06-简历与求职/04-09-求职追踪.md"),
    ("./10-面试与晋升素材库.md", "../../21-Interview/01-面试方法论/06-10-面试与晋升素材库.md"),
    ("../05-AI工程/", "../../18-AI-Engineering/"),
    ("../06-C++嵌入式/", "../../19-Cpp/01-语言与嵌入式/"),
    ("../01-Java/", "../../01-Java/"),
    ("../README.md", "../../README.md"),
]

LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def should_skip(path: Path) -> bool:
    try:
        path.relative_to(SKIP)
        return True
    except ValueError:
        return False


def fix_content(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def main() -> None:
    changed = 0
    for md in ROOT.rglob("*.md"):
        if should_skip(md):
            continue
        original = md.read_text(encoding="utf-8")
        updated = fix_content(original)
        if updated != original:
            md.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"fixed: {md.relative_to(ROOT)}")
    print(f"Done. {changed} files updated.")


if __name__ == "__main__":
    main()
