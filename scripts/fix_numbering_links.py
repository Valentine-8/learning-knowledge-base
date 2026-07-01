# -*- coding: utf-8 -*-
"""Fix double-prefix corruption and update relative folder links after numbering."""
import re
from pathlib import Path

ROOT = Path(r"d:\学习")

TEXT_FIXES = [
    ("03-ConcurrentHashMap", "03-ConcurrentHashMap"),
    ("ConcurrentHashMap", "ConcurrentHashMap"),
    ("01-List与ArrayList", "01-List与ArrayList"),
    ("01-阅读指南", "01-阅读指南"),
    ("01-扩展技能全景", "01-扩展技能全景"),
    ("02-7年工程师技能全景索引", "02-7年工程师技能全景索引"),
    ("03-7年Java工程师学习路线", "03-7年Java工程师学习路线"),
    ("01-7年Java工程师技能清单", "01-7年Java工程师技能清单"),
    ("04-java学习", "04-java学习"),
    ("05-简历", "05-简历"),
    ("06-项目经历面试手册", "06-项目经历面试手册"),
    ("07-面试题大全Q&A", "07-面试题大全Q&A"),
    ("08-面试前速查", "08-面试前速查"),
    ("09-系统设计练手", "09-系统设计练手"),
    ("01-Python/16-复习手册", "01-Python/16-复习手册"),
    ("01-Python/99-附录-Java与Python对照", "01-Python/99-附录-Java与Python对照"),
]

# (pattern, replacement) — regex, only unnumbered folder segments
FOLDER_PATTERNS: list[tuple[str, str]] = [
    (r"(?<!\d-)(?<=[\./])集合/", "01-集合/"),
    (r"(?<!\d-)(?<=[\./])JVM/", "02-JVM/"),
    (r"(?<!\d-)(?<=[\./])并发/", "03-并发/"),
    (r"(?<!\d-)(?<=[\./])Spring/", "04-Spring/"),
    (r"(?<!\d-)(?<=[\./])SpringCloud/", "05-SpringCloud/"),
    (r"(?<!\d-)(?<=[\./])JPA/", "06-JPA/"),
    (r"(?<!\d-)(?<=[\./])WebFlux/", "07-WebFlux/"),
    (r"(?<!\d-)(?<=[\./])分布式/", "08-分布式/"),
    (r"(?<!\d-)(?<=[\./])架构/", "09-架构/"),
    (r"(?<!\d-)(?<=[\./])Maven与Gradle/", "10-Maven与Gradle/"),
    (r"(?<!\d-)(?<=[\./])测试/", "11-测试/"),
    (r"(?<!\d-)(?<=[\./])压测/", "12-压测/"),
    (r"(?<!\d-)(?<=[\./])MySQL/", "01-MySQL/"),
    (r"(?<!\d-)(?<=[\./])PostgreSQL/", "02-PostgreSQL/"),
    (r"(?<!\d-)(?<=[\./])Redis/", "03-Redis/"),
    (r"(?<!\d-)(?<=[\./])消息队列/", "04-消息队列/"),
    (r"(?<!\d-)(?<=[\./])Elasticsearch/", "05-Elasticsearch/"),
    (r"(?<!\d-)(?<=[\./])MongoDB/", "06-MongoDB/"),
    (r"(?<!\d-)(?<=[\./])gRPC/", "07-gRPC/"),
    (r"(?<!\d-)(?<=[\./])ZooKeeper/", "08-ZooKeeper/"),
    (r"(?<!\d-)(?<=[\./])大数据/", "09-大数据/"),
    (r"(?<!\d-)(?<=[\./])Linux/", "01-Linux/"),
    (r"(?<!\d-)(?<=[\./])Shell/", "02-Shell/"),
    (r"(?<!\d-)(?<=[\./])Git/", "03-Git/"),
    (r"(?<!\d-)(?<=[\./])Nginx/", "04-Nginx/"),
    (r"(?<!\d-)(?<=[\./])Docker/", "05-Docker/"),
    (r"(?<!\d-)(?<=[\./])Kubernetes/", "06-Kubernetes/"),
    (r"(?<!\d-)(?<=[\./])CI-CD/", "07-CI-CD/"),
    (r"(?<!\d-)(?<=[\./])可观测性/", "08-可观测性/"),
    (r"(?<!\d-)(?<=[\./])云平台/", "09-云平台/"),
    (r"(?<!\d-)(?<=[\./])算法与数据结构/", "01-算法与数据结构/"),
    (r"(?<!\d-)(?<=[\./])计算机网络/", "02-计算机网络/"),
    (r"(?<!\d-)(?<=[\./])操作系统/", "03-操作系统/"),
    (r"(?<!\d-)(?<=[\./])安全/", "04-安全/"),
    (r"(?<!\d-)(?<=[\./])Python/", "01-Python/"),
    (r"(?<!\d-)(?<=[\./])Go/", "02-Go/"),
]


def apply_folder_fixes(text: str) -> str:
    for pattern, repl in FOLDER_PATTERNS:
        text = re.sub(pattern, repl, text)
    return text


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".ps1", ".json"}:
            continue
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        original = text
        for old, new in sorted(TEXT_FIXES, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
        text = apply_folder_fixes(text)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
            print(path.relative_to(ROOT))
    print(f"\nFixed {changed} files.")


if __name__ == "__main__":
    main()
