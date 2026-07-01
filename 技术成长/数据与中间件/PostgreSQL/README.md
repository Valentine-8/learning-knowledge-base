# PostgreSQL 深度学习（MVCC · JSON · 生产级）

> **适用**：7 年 Java 后端 — 新项目选型、与 MySQL 对比、JSON/GIS、面试。
> **读法**：约 12～15h；复习先看 [00-速查总览](./00-速查总览.md)。

---

## 章节目录

| 章 | 文档 | 核心内容 | 预计 |
|:--:|------|----------|:----:|
| 00 | [速查总览](./00-速查总览.md) | 架构一图 + 与 MySQL 对比 + 面试 5 分钟 | 10 min |
| 01 | [架构与 MVCC](./01-架构与MVCC.md) | 进程模型、Heap、MVCC、VACUUM | 60 min |
| 02 | [索引与执行计划](./02-索引与执行计划.md) | B-tree、GIN、GiST、EXPLAIN ANALYZE | 60 min |
| 03 | [JSON 与高级类型](./03-JSON与高级类型.md) | JSONB、数组、全文检索、扩展 | 50 min |
| 04 | [事务锁与并发](./04-事务锁与并发.md) | 隔离级别、行锁、死锁、SKIP LOCKED | 50 min |
| 05 | [复制与高可用](./05-复制与高可用.md) | 流复制、逻辑复制、Patroni 了解 | 40 min |
| 06 | [与 MySQL 对比选型](./06-与MySQL对比选型.md) | 语法差异、迁移、场景选型 | 40 min |
| 07 | [生产案例与面试题库](./07-生产案例与面试题库.md) | 故障案例、50+ 面试题 | 60 min |

---

## 配套

- MySQL 对照：[MySQL/README](../MySQL/README.md)
- Java 数据源：`spring.datasource` + HikariCP 配置相同
- Phase5：[phase5-数据库](../../Java/笔记/phase5-数据库/复习手册.md)

← [数据与中间件](../README.md)
