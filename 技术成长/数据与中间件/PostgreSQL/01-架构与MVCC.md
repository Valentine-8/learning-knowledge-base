# 01 · 架构与 MVCC

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 进程模型

PostgreSQL 采用 **每连接一进程**（非 MySQL 线程池）：

```
Postmaster
  ├── Backend: 连接 1 → 处理 SQL
  ├── Backend: 连接 2
  ├── Background Writer
  ├── WAL Writer
  ├── Checkpointer
  └── Autovacuum Launcher → Worker(s)
```

| 特点 | 说明 |
|------|------|
| 隔离好 | 连接崩溃不影响其他 |
| 内存 | 每连接有 work_mem 等，连接数多要控 |
| Java | HikariCP 池化，避免直连过多 |

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20   # 不是越大越好
```

---

## 2. 存储结构

| 概念 | 说明 |
|------|------|
| Database | 库，隔离 namespace |
| Schema | 模式，默认 `public` |
| Table / Index | 堆表 + 独立索引文件 |
| Tablespace | 表空间，指定磁盘 |
| OID | 对象内部 ID |

**与 InnoDB**：PG **没有聚簇索引**，表是堆，PK 也是普通唯一 B-tree 索引。

```
INSERT 顺序 → 堆上物理无序
PK 索引     →  (id) → 行指针 (ctid)
二级索引    →  (col) → ctid → 回表
```

---

## 3. MVCC 核心

每行有系统列：

| 列 | 含义 |
|----|------|
| `xmin` | 插入/更新该行的事务 ID |
| `xmax` | 删除/更新该行的事务 ID（0 表示未删） |
| `ctid` | 物理位置（页号,行号） |

**UPDATE** = INSERT 新版本 + 旧行标记 xmax（**不原地更新**）。

**快照（Snapshot）**：事务开始时可见哪些 xmin/xmax 组合。

```
事务 100 快照：所有 committed 且 xmin < 100 且 (xmax=0 或 xmax 未提交或 xmax>100)
→ 读不加锁，写行锁
```

---

## 4. 隔离级别

| 级别 | PG 行为 |
|------|---------|
| Read Uncommitted | 实际等同 RC（PG 不读脏） |
| **Read Committed**（默认） | 每条语句新快照 |
| Repeatable Read | 事务级快照，PG 防幻读（SSI 增强） |
| Serializable | 真串行化，检测冲突 |

**与 MySQL RR**：MySQL InnoDB RR + MVCC 默认防幻读（间隙锁）；PG RR 用 **SSI（Serializable Snapshot Isolation）** 机制不同。

---

## 5. WAL 与 Checkpoint

类似 InnoDB Redo：

```
写数据 → 先写 WAL（顺序 IO）→ 刷 shared buffers → 异步 checkpoint 落盘
```

| 参数 | 作用 |
|------|------|
| `wal_level` | replica / logical |
| `max_wal_size` | WAL 触发 checkpoint |
| `checkpoint_timeout` | 定时 checkpoint |

**崩溃恢复**：重放 WAL。

---

## 6. VACUUM 与 Autovacuum

DELETE/UPDATE 留下 **dead tuple**，不 vacuum 则：

- 表 **膨胀**（bloat）
- 索引膨胀
- **Transaction ID wraparound** 致命风险

```sql
VACUUM orders;           -- 回收空间（通常不还给 OS）
VACUUM FULL orders;      -- 锁表重写，回收 OS 空间，慎用
ANALYZE orders;          -- 更新统计信息给优化器
```

**Autovacuum**：后台自动；长事务会阻止 vacuum 清理旧版本 → **表越来越胖**。

```sql
SELECT pid, state, query, xact_start
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY xact_start;
```

---

## 7. 连接与内存

| 参数 | 说明 |
|------|------|
| `shared_buffers` | 共享缓存，通常内存 25% |
| `work_mem` | 排序/Hash 每操作内存 |
| `maintenance_work_mem` | VACUUM/CREATE INDEX |
| `max_connections` | 最大连接 |

**估算**：`max_connections × work_mem` 不能爆内存。

---

## 8. Java 侧注意

```java
// PG 推荐 JDBC batch
PreparedStatement ps = conn.prepareStatement("INSERT INTO t(a) VALUES (?)");
for (...) { ps.setString(1, v); ps.addBatch(); }
ps.executeBatch();

// PG 支持 RETURNING
INSERT INTO orders (...) VALUES (...) RETURNING id;
```

---

## 9. 面试题

| 问 | 答 |
|----|-----|
| PG MVCC 与 InnoDB？ | 都是多版本；PG 堆表+系统列；InnoDB 聚簇+Undo |
| 为何 UPDATE 慢？ | 写新版本+索引更新+dead tuple |
| VACUUM 必须吗？ | 必须，PG 无 undo 自动 purge 同 MySQL |
| 每连接一进程利弊？ | 稳但连接数受限，要池化 |

---

→ [02-索引与执行计划](./02-索引与执行计划.md)

← [速查总览](./00-速查总览.md)
