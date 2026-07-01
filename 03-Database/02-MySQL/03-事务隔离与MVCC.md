# 03 · 事务隔离与 MVCC

> **适用**：7 年 Java 后端 · InnoDB 事务语义 · 面试深挖 · 线上长事务治理  
> **前置**：[01-InnoDB架构与日志体系](./01-InnoDB架构与日志体系.md)（Undo Log）、[02-索引原理与B+树](./02-索引原理与B+树.md)  
> **后续**：[04-锁机制与死锁](./04-锁机制与死锁.md)（间隙锁、Next-Key Lock 细节）

---

## 一、ACID 详解

事务（Transaction）是 InnoDB 将一组 SQL 作为一个逻辑单元执行的机制。ACID 是衡量事务可靠性的四个属性。

### 1.1 四属性对照表

| 属性 | 英文 | 含义 | InnoDB 实现要点 | 违反时的典型现象 |
|------|------|------|-----------------|------------------|
| **原子性** | Atomicity | 全部成功或全部失败 | **Undo Log** 记录修改前镜像，回滚时按 Undo 逆序恢复 | 部分更新成功、数据不一致 |
| **一致性** | Consistency | 事务前后满足业务约束（主键唯一、外键、余额非负等） | 由应用 + DB 约束共同保证；ACID 中 C 是目标，AID 是手段 | 超卖、余额为负 |
| **隔离性** | Isolation | 并发事务互不干扰（程度由隔离级别决定） | **MVCC + 锁** | 脏读、不可重复读、幻读 |
| **持久性** | Durability | 提交后即使崩溃也不丢 | **Redo Log** WAL，崩溃恢复重放 | 提交后数据丢失 |

### 1.2 原子性：Undo Log 与回滚

```sql
-- 示例：转账事务
START TRANSACTION;
UPDATE account SET balance = balance - 100 WHERE id = 1;  -- A 扣款
UPDATE account SET balance = balance + 100 WHERE id = 2;  -- B 加款
-- 若此处抛异常或 ROLLBACK
COMMIT;
```

**过程**：
1. 每次 UPDATE 在修改数据页前，先把旧值写入 **Undo Log**（逻辑日志）。
2. `ROLLBACK` 或崩溃恢复时，按 Undo 链把行恢复到事务开始前的版本。
3. 原子性只保证「这条语句要么全做要么全不做」，**不保证业务一致性**（例如只扣 A 不加 B 若没在同一事务里则无法原子）。

### 1.3 一致性：谁的责任？

```
┌─────────────────────────────────────────────────────────┐
│  应用层：库存 ≥ 0、订单状态机合法、幂等键                  │
│  DB 层：PRIMARY KEY、UNIQUE、CHECK、FOREIGN KEY          │
│  事务：把多个写操作绑在一起，避免中间态被其他会话看到       │
└─────────────────────────────────────────────────────────┘
```

**生产案例**：电商扣库存 — 若 `UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty >= 1` 不在事务内，或隔离级别过低导致读到脏数据，会出现超卖。一致性需要 **WHERE 条件 + 事务 + 合适隔离级别** 共同保障。

### 1.4 隔离性：并发控制的两大支柱

| 机制 | 适用读类型 | 核心思想 |
|------|-----------|----------|
| **MVCC** | 快照读（普通 SELECT） | 读历史版本，不加锁，高并发 |
| **锁** | 当前读（SELECT FOR UPDATE、UPDATE、DELETE） | 读最新已提交版本并加锁 |

### 1.5 持久性：Redo 与两阶段提交

提交时：**prepare Redo → 写 Binlog → commit Redo**。详见 [01 章](./01-InnoDB架构与日志体系.md)。  
面试常问：**为什么有了 Binlog 还要 Redo？** — Redo 负责崩溃恢复（物理页级、InnoDB 内部）；Binlog 负责复制与归档（逻辑/半逻辑、Server 层）。二者通过 **XID** 关联。

---

## 二、隔离级别与并发异常

SQL 标准定义四种隔离级别；MySQL InnoDB 默认 **REPEATABLE READ（RR）**。

### 2.1 三种读现象

| 现象 | 英文 | 定义 | 举例 |
|------|------|------|------|
| **脏读** | Dirty Read | 读到**未提交**的其他事务修改 | T2 读到 T1 未 commit 的余额 |
| **不可重复读** | Non-Repeatable Read | **同一事务内**两次读同一行，结果不同（他事务 **UPDATE 并提交**） | 两次查余额 100 → 80 |
| **幻读** | Phantom Read | **同一事务内**两次范围读，**行数**变化（他事务 **INSERT/DELETE 并提交**） | 两次 `SELECT * WHERE status=1` 行数不同 |

> **注意**：InnoDB 在 RR 下对**快照读**通过 MVCC 避免幻读；对**当前读**仍可能幻读，需 **Next-Key Lock**（见 [04 章](./04-锁机制与死锁.md)）。

### 2.2 四种隔离级别矩阵

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | InnoDB 实现摘要 |
|----------|:----:|:----------:|:----:|-----------------|
| READ UNCOMMITTED | ✓ 可能 | ✓ | ✓ | 几乎不用，读最新版本不加 Read View |
| READ COMMITTED | ✗ | ✓ 可能 | ✓ 可能 | 每次 SELECT 生成新 Read View |
| **REPEATABLE READ**（默认） | ✗ | ✗ | 快照读 ✗；当前读需锁 | 事务首次一致性读生成 Read View |
| SERIALIZABLE | ✗ | ✗ | ✗ | 普通 SELECT 也加共享锁，性能差 |

```sql
-- 查看与修改隔离级别
SELECT @@transaction_isolation;          -- 8.0+
-- SELECT @@tx_isolation;                -- 5.7
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

### 2.3 RC vs RR 行为对比（实验）

**表**：`t(id PK, k INT)`，初始 `(1,1), (2,2)`。

```sql
-- 会话 A（RR）
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
START TRANSACTION;
SELECT k FROM t WHERE id = 1;  -- 结果 1

-- 会话 B
START TRANSACTION;
UPDATE t SET k = 10 WHERE id = 1;
COMMIT;

-- 会话 A 再次
SELECT k FROM t WHERE id = 1;  -- RR: 仍 1（快照读）
COMMIT;
```

若 A 为 **RC**：第二次 SELECT 结果为 **10**（新 Read View）。

### 2.4 幻读演示与 InnoDB 的特殊处理

```sql
-- 会话 A（RR）
START TRANSACTION;
SELECT * FROM orders WHERE user_id = 100 AND status = 'PENDING';  -- 0 行

-- 会话 B
INSERT INTO orders (user_id, status) VALUES (100, 'PENDING');
COMMIT;

-- 会话 A
SELECT * FROM orders WHERE user_id = 100 AND status = 'PENDING';  -- 仍 0 行（快照读，无幻读）

-- 但若 A 执行当前读：
SELECT * FROM orders WHERE user_id = 100 AND status = 'PENDING' FOR UPDATE;  -- 可能看到 1 行
-- 或在 RR 下先快照读再 UPDATE 同一范围，会触发间隙锁（04 章）
```

---

## 三、MVCC 多版本并发控制

MVCC（Multi-Version Concurrency Control）让**读不阻塞写、写不阻塞读**（快照读路径），通过保留行的多个版本 + Read View 决定可见性。

### 3.1 隐藏列与版本链

InnoDB 每行额外存储（概念上）：

| 字段 | 大小 | 含义 |
|------|------|------|
| `DB_TRX_ID` | 6 字节 | 最后修改该行的事务 ID |
| `DB_ROLL_PTR` | 7 字节 | 回滚指针，指向 Undo Log 中上一版本 |
| `DB_ROW_ID` | 6 字节 | 隐藏主键（无显式 PK 时） |

**版本链示意**：

```
当前行 (k=30, trx_id=300)
    │ roll_pointer
    ▼
Undo: (k=20, trx_id=200)
    │ roll_pointer
    ▼
Undo: (k=10, trx_id=100)
```

事务读取时沿 **roll_pointer → undo chain** 回溯，找到对当前 Read View **可见**的最新版本。

### 3.2 事务 ID 分配

- `trx_id` 单调递增，在事务**第一次修改**（INSERT/UPDATE/DELETE）时分配。
- 只读事务可能不分配 trx_id（8.0 优化）。
- **Read View** 在事务第一次 **一致性读**（快照读）时创建，RR 下复用；RC 下每条 SELECT 新建。

### 3.3 Read View 结构

Read View 是 MVCC 的核心，决定「哪些 trx_id 的修改对我可见」。

| 字段 | 含义 |
|------|------|
| `m_ids` | 创建 Read View 时，系统中**活跃（未提交）**的事务 ID 列表 |
| `min_trx_id` | `m_ids` 中最小值；`< min_trx_id` 的事务已提交，其修改**可见** |
| `max_trx_id` | 下一个将要分配的事务 ID；`≥ max_trx_id` 的事务在 View 创建后开始，其修改**不可见** |
| `creator_trx_id` | 创建该 Read View 的事务自身 ID |

**可见性规则**（对某行版本的 `trx_id = tid`）：

```
1. tid == creator_trx_id     → 可见（自己的修改）
2. tid < min_trx_id          → 可见（已提交且早于活跃集）
3. tid >= max_trx_id         → 不可见（Read View 之后才开始）
4. min_trx_id ≤ tid < max_trx_id：
   - tid ∈ m_ids            → 不可见（未提交）
   - tid ∉ m_ids            → 可见（已提交）
5. 不可见则沿 roll_pointer 读上一版本，重复判断
```

**图示**：

```
时间轴 ──────────────────────────────────────────────►
         │◄── 已提交且可见 ──►│◄─ m_ids 活跃 ─►│ 未来事务
trx_id:  1   2   3   4   5   6   7   8   9  [10]
                              min=6    max=10
                              m_ids={6,8}
```

### 3.4 快照读完整流程

```sql
-- 会话 A, trx_id=100, RR
START TRANSACTION;
SELECT * FROM t WHERE id = 1;
```

1. 首次 SELECT → 创建 Read View（假设 min=50, max=105, m_ids={102,103}, creator=100）。
2. 读 id=1 行，DB_TRX_ID=103 ∈ m_ids → 不可见。
3. 沿 roll_pointer 找到 trx_id=80 的版本 → 80 < min → **可见**，返回该版本。
4. 后续 SELECT **复用同一 Read View**（RR），结果一致 → **避免不可重复读**。

---

## 四、快照读 vs 当前读

| 对比项 | 快照读（Consistent Read） | 当前读（Current Read） |
|--------|---------------------------|------------------------|
| SQL 示例 | 普通 `SELECT` | `SELECT ... FOR UPDATE/SHARE`、`UPDATE`、`DELETE`、`INSERT` |
| 读到的版本 | Read View 可见的历史版本 | **最新已提交**版本（并加锁） |
| 是否加锁 | 否（一致性非锁定读） | 是（记录锁/间隙锁/Next-Key） |
| 幻读 | RR 下 MVCC 避免 | 需 Next-Key Lock 避免 |
| 典型场景 | 报表、列表查询 | 扣库存、抢单、悲观锁 |

```sql
-- 当前读示例
START TRANSACTION;
SELECT stock FROM product WHERE id = 1 FOR UPDATE;  -- 加 X 锁，读最新
UPDATE product SET stock = stock - 1 WHERE id = 1;
COMMIT;
```

**混合使用陷阱**：

```sql
START TRANSACTION;
SELECT * FROM orders WHERE id = 1;              -- 快照读，可能读到旧 status
UPDATE orders SET status = 'PAID' WHERE id = 1; -- 当前读，若 status 已被改可能 0 rows affected
COMMIT;
```

生产建议：先 `FOR UPDATE` 锁定再业务判断，或使用 **乐观锁** `UPDATE ... WHERE id=? AND version=?`。

---

## 五、一致性非锁定读（Consistent Non-locking Read）

InnoDB 文档术语：**Consistent Read** = 利用 MVCC 读快照，**不加锁**，不阻塞其他事务对同一行的写（当前读仍会阻塞）。

### 5.1 与 Locking Read 对比

| 类型 | 别名 | 阻塞关系 |
|------|------|----------|
| Consistent Non-locking Read | 快照读 | 不阻塞写；不被 X 锁阻塞 |
| Locking Read | 当前读 | 与 X/S 锁互斥规则见 04 章 |

### 5.2 auto-commit 下的快照读

```sql
SET autocommit = 1;
SELECT * FROM t;  -- 每条语句隐式单语句事务，仍走 MVCC（RC 下每条新 View）
```

### 5.3 READ ONLY 事务

```sql
START TRANSACTION READ ONLY;
SELECT ...;  -- 只快照读，InnoDB 可优化（8.0 只读事务不分配 undo 等）
COMMIT;
```

---

## 六、RR 如何防止幻读（与 04 章衔接）

标准 **幻读** 定义针对同一事务内重复**范围查询**结果集行数变化。

InnoDB RR 策略是 **双轨制**：

| 读类型 | 防幻读机制 |
|--------|-----------|
| 快照读 | MVCC：Read View 固定，新 INSERT 行的 trx_id 不可见 |
| 当前读 | **Next-Key Lock**（记录锁 + 间隙锁）锁住索引记录及间隙，阻塞范围内 INSERT |

```sql
-- 会话 A
START TRANSACTION;
SELECT * FROM t WHERE id >= 5 AND id < 10 FOR UPDATE;  -- Next-Key Lock on gaps

-- 会话 B
INSERT INTO t(id) VALUES(7);  -- 阻塞，直到 A 提交
```

**注意**：若 `id` 无索引，可能锁全表（见 04 章）。  
**快照读不防「当前读语境下的幻读」**：若只用普通 SELECT，其他事务 INSERT 并提交，你仍看不到；但若随后 `FOR UPDATE` 同一范围，会看到新行 — 这不是 MVCC 意义上的幻读，而是读类型切换。

→ 间隙锁、Next-Key Lock、Insert Intention Lock 详见 **[04-锁机制与死锁](./04-锁机制与死锁.md)**。

---

## 七、Undo Log 与 MVCC 的回收

- 多版本存在 Undo 链中；**无 Read View 再需要**的旧版本才可 purge。
- **长事务**持有旧 Read View → 阻止 purge → Undo 膨胀 → 见下一节。

```sql
-- 查看 Undo 表空间（8.0）
SELECT NAME, STATE FROM information_schema.INNODB_TABLESPACES
WHERE NAME LIKE '%undo%';
```

---

## 八、长事务危害（生产重点）

### 8.1 危害清单

| 危害 | 机制 | 线上表现 |
|------|------|----------|
| Undo 堆积 | 旧版本无法 purge | 磁盘涨、ibdata/undo 表空间变大 |
| 锁持有久 | 当前读持 X 锁 | 阻塞、线程堆积、`Lock wait timeout` |
| 主从延迟 | 大事务 Binlog 一次回放 | 从库 seconds_behind_master 飙升 |
| 复制中断风险 | 单事务过大 | relay log 应用慢 |
| 连接池耗尽 | 事务未提交占连接 | 应用 `Cannot get connection` |
| MVCC 读性能下降 | 版本链过长 | 单次 SELECT 回溯多层 Undo |

### 8.2 发现长事务

```sql
-- 运行超过 60s 的事务
SELECT trx_id, trx_started, trx_mysql_thread_id, trx_query,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_sec
FROM information_schema.innodb_trx
WHERE TIMESTAMPDIFF(SECOND, trx_started, NOW()) > 60
ORDER BY trx_started;

-- 8.0 performance_schema
SELECT * FROM performance_schema.events_transactions_current
WHERE STATE = 'ACTIVE' AND TIMER_WAIT > 60*1e12;
```

### 8.3 生产案例：报表拖垮库

**场景**：运营后台 `START TRANSACTION` 后跑大报表（5 分钟），同一连接 autocommit=0。  
**后果**：trx 不释放 → Undo 无法清理 → 其他会话 UPDATE 变慢；若报表含 `FOR UPDATE` 则锁等待激增。  
**治理**：
- 报表只读从库，`READ ONLY` 或 RC + 无事务包裹；
- 应用层事务超时（Spring `@Transactional(timeout=30)`）；
- 监控 `innodb_trx` age，告警 > 30s；
- 拆分批量任务为小批次 commit。

### 8.4 Java 侧常见根因

| 根因 | 说明 |
|------|------|
| `@Transactional` 套大循环 | 整个循环在一个 trx 里 |
| 事务内调 RPC/HTTP | 外部慢导致 trx 拉长 |
| 异常未抛出 | 未 rollback 但连接归还池，下次复用脏 trx |
| 批量 job 未分批 commit | 一次更新百万行 |

---

## 九、隔离级别选型建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| 默认 OLTP | RR | InnoDB 优化好；快照读性能高 |
| Oracle 迁移 / 少锁冲突 | RC | 间隙锁少；每次读最新已提交 |
| 金融对账 | RR + 当前读显式锁 | 业务需可重复读 + 防并发写 |
| 只读统计 | 从库 + RC 或无 trx | 避免长 MVCC 链 |

```sql
-- 仅当前会话改 RC（常见于阿里规范部分业务）
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

---

## 十、面试 Q&A（18 题）

### Q1：ACID 分别靠什么实现？

**A**：A-Undo 回滚；C-约束+应用；I-MVCC+锁；D-Redo WAL。一致性是目标不是单一机制。

### Q2：RR 和 RC 在 Read View 上的区别？

**A**：RC 每条 SELECT 新建 Read View，能读到已提交新值 → 不可重复读。RR 首次一致性读创建 View 并复用 → 快照读结果一致。

### Q3：MVCC 能否完全代替锁？

**A**：不能。快照读无写冲突检测；`UPDATE stock` 类场景必须当前读 + 锁或乐观锁/version 列。

### Q4：什么是幻读？InnoDB RR 完全解决了吗？

**A**：同一事务内重复范围读行数变化。RR 下快照读无幻读；当前读靠 Next-Key Lock。严格说标准幻读针对快照读，InnoDB 已解决。

### Q5：trx_id 何时分配？

**A**：事务第一次执行修改语句时。纯只读可能无 trx_id（8.0）。

### Q6：Read View 的 max_trx_id 是什么？

**A**：分配 Read View 时系统「下一个将分配的事务 ID」，不是最大活跃 ID。≥ max 的事务修改不可见。

### Q7：为什么 RC 间隙锁更少？

**A**：RC 下半一致性读、删除仅记录锁等优化；且许多场景不需要防幻读间隙锁（RC 不承诺防幻读）。

### Q8：SELECT 加 FOR UPDATE 走 MVCC 吗？

**A**：不走。是当前读，读最新版本并加 X 锁。

### Q9：Undo Log 太大怎么排查？

**A**：查 `innodb_trx` 长事务、历史列表长度 `SHOW ENGINE INNODB STATUS\G` 的 History list length；杀长 trx 或等 purge。

### Q10：Serializable 为什么慢？

**A**：普通 SELECT 自动 `LOCK IN SHARE MODE`，读写互斥严重。

### Q11：主从复制与隔离级别有关吗？

**A**：从库重放 Binlog 是串行的；主库 RR 长事务导致 Binlog 事件延迟写入，间接影响复制延迟。

### Q12：能否在事务中切换隔离级别？

**A**：`SET SESSION` 影响后续新事务；当前 trx 部分版本需重启事务才完全生效，生产不推荐 trx 内切换。

### Q13：快照读能读到自己的未提交修改吗？

**A**：能。creator_trx_id 规则使本事务修改对自己可见（即使未 commit，在 trx 内 SELECT 能看到）。

### Q14：什么是半一致性读（Semi-consistent Read）？

**A**：RC 下 UPDATE 遇锁时，InnoDB 可读最新已提交版本判断是否满足 WHERE，减少锁等待（仅 RC）。

### Q15：两阶段提交与 MVCC 关系？

**A**：无直接关系。2PC 保证 Redo+Binlog 一致；MVCC 用 Undo 版本链。提交后 trx_id 才对其他事务 Read View 可见。

### Q16：Java `@Transactional(isolation=READ_COMMITTED)` 何时用？

**A**：减少间隙锁死锁、需读最新已提交（如部分库存展示）；需评估不可重复读业务影响。

### Q17：purge 线程做什么？

**A**：清理已无事务需要的 Undo 版本；长 trx 阻塞 purge → Undo 膨胀。

### Q18：如何验证当前会话隔离级别？

**A**：`SELECT @@transaction_isolation;` 或 `SHOW VARIABLES LIKE 'transaction_isolation';`

---

## 十一、本章小结

```
                    ┌──────────────┐
                    │   ACID       │
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
        Undo(R)         MVCC+Lock        Redo(D)
           │               │
           │         ┌─────┴─────┐
           │         ▼           ▼
           │    快照读       当前读
           │   Read View    锁(04章)
           └──────────────────────────► 一致性
```

| 必记 | 内容 |
|------|------|
| 默认隔离级别 | RR |
| MVCC 四元组 | m_ids, min_trx_id, max_trx_id, creator_trx_id |
| 幻读 | 快照读 MVCC；当前读 Next-Key |
| 长事务 | Undo 膨胀、锁、主从延迟 |

---

## 导航

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [02-索引原理与B+树](./02-索引原理与B+树.md) | [MySQL README](./README.md) | [04-锁机制与死锁](./04-锁机制与死锁.md) |

↑ [数据与中间件](../../README.md)
