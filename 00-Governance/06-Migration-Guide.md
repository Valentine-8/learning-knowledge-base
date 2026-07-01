# Migration Guide

## 1. 迁移概述

**日期**：2026-07-01  
**依据**：[Repository-Specification.md](./01-Repository-Specification.md)、[Repository-Structure.md](./02-Repository-Structure.md)

将原 ``、`前端/`、`奥林巴斯ep7/` 结构重组为编号英文顶层目录，按知识体系而非学习阶段组织。

## 2. 主要映射

| 原路径 | 新路径 |
|--------|--------|
| `03-Database/02-MySQL/` | `03-Database/02-MySQL/` |
| `04-Redis/` | `04-Redis/` |
| `05-Message-Queue/` | `05-Message-Queue/` |
| `06-Middleware/01-Elasticsearch/` | `06-Middleware/01-Elasticsearch/` |
| `16-Computer-Science/*` | `16-Computer-Science/*` |
| `18-AI-Engineering/` | `18-AI-Engineering/` |
| `01-Java/03-集合框架/` | `01-Java/03-集合框架/` |
| `01-Java/笔记/phase2~8` | `08-JVM/`、`09-Concurrency/` 等对应域 |
| `90-Growth/01-学习方法/` | `90-Growth/` + `21-Interview/` |
| `19-Cpp/01-语言与嵌入式/` | `19-Cpp/` + `21-Interview/` |
| `99-Archive/Frontend-Demos/Vue2-Basic/` | `99-Archive/Frontend-Demos/Vue2-Basic/` |
| `98-Personal-Topics/Photography/Olympus-EP7/` | `98-Personal-Topics/Photography/Olympus-EP7/` |
| 原 `` 残余 | `99-Archive/Legacy-Technical-Growth/` |

完整映射见 [02-Repository-Structure.md](./02-Repository-Structure.md) 第 28 节。

## 3. 后续工作

1. Phase 复习手册按「一文一题」拆分为独立专题文档。
2. 补齐 `02-Spring-Ecosystem`、`07-Microservices` 等待建模块。
3. `17-Frontend/` 按 Vue3 正式知识体系重建（旧 Vue2 Demo 仅作归档参考）。
4. 运行 `scripts/fix_links.py` 后人工抽查关键导航链接。

## 4. 工具

- `scripts/migrate_to_spec.py`：目录迁移脚本
- `scripts/fix_links.py`：批量修复 Markdown 链接
