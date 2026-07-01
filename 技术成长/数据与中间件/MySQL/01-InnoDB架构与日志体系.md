# 01 · InnoDB 架构与日志体系

> **目标读者**：7 年 Java 后端工程师，需能讲清 InnoDB 内存/磁盘结构、三种日志职责、刷盘策略与两阶段提交，并在面试与线上故障中快速定位问题。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 总览：InnoDB 在 MySQL 中的位置

```
┌─────────────────────────────────────────────────────────────────┐
│                        MySQL Server Layer                       │
│   连接器 · 解析器 · 优化器 · 执行器 · SQL 接口                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ 调用存储引擎 API
┌────────────────────────────▼────────────────────────────────────┐
│                     InnoDB Storage Engine                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Memory 结构   │  │ Disk 结构     │  │ 日志体系              │ │
│  │ Buffer Pool  │  │ Tablespace   │  │ Redo · Undo · Binlog │ │
│  │ Change Buffer│  │ .ibd 数据文件 │  │ 两阶段提交            │ │
│  │ AHI · Log Buf│  │ Doublewrite  │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

InnoDB 是 MySQL 8.0 默认存储引擎，支持**事务、行级锁、外键、崩溃恢复（Crash Recovery）**。Java 后端日常接触的 OLTP 业务几乎清一色 InnoDB。

---

## 2. InnoDB vs MyISAM

| 维度 | InnoDB | MyISAM |
|------|--------|--------|
| 事务 | 支持 ACID | 不支持 |
| 锁粒度 | 行级锁 + 意向锁 | 表级锁 |
| 崩溃恢复 | Redo Log 保证 | 易损坏，需 repair |
| 索引结构 | 聚簇索引（数据与主键同文件） | 非聚簇（索引与数据分离） |
| 外键 | 支持 | 不支持 |
| 全文索引 | 8.0 起支持 | 原生支持（历史优势） |
| 适用场景 | OLTP、高并发写、需要事务 | 只读报表、日志归档（已边缘化） |

**生产结论**：MySQL 5.7+ / 8.0 新项目一律 InnoDB。MyISAM 仅出现在遗留系统或特殊只读场景。

**真实场景**：某报表库从 MyISAM 迁到 InnoDB 后，并发导入不再因表锁导致全站写入阻塞；但单表全表扫描速度可能略降（聚簇索引顺序读 vs MyISAM 堆文件）。

---

## 3. 内存结构

### 3.1 Buffer Pool（缓冲池）

Buffer Pool 是 InnoDB 最重要的内存组件，默认约占 `innodb_buffer_pool_size`（生产常见设为物理内存 60%～75%）。

**Page（页）**：InnoDB 数据读写的最小单位，默认 **16KB**（`innodb_page_size`，一般不改）。

```
                    Buffer Pool (LRU List)
    ┌──────────────────────────────────────────────────────┐
    │  young 区 (5/8)          │  old 区 (3/8)             │
    │  热点页，新读入先放 old  │  读一次仍在 old，再读晋升   │
    │  ┌───┬───┬───┬───┐      │  ┌───┬───┐                 │
    │  │ P │ P │ P │...│ ←─── │  │ P │ P │ ...             │
    │  └───┴───┴───┴───┘      │  └───┴───┘                 │
    └──────────────────────────────────────────────────────┘
              ↑
         Flush List（脏页链表，按 LSN 排序，Checkpoint 推进依据）
```

**LRU 优化（避免全表扫描污染）**：

- 新页首次插入 **old 区头部**（midpoint insertion）。
- 在 old 区停留超过 `innodb_old_blocks_time`（默认 1s）且再次被访问，才进入 young 区。
- 全表扫描的大结果集不会把热点页全部挤出。

**Flush List**：被修改但未刷盘的脏页链表，每个脏页关联最后修改它的 **LSN（Log Sequence Number）**。Checkpoint 推进时，LSN 小于 checkpoint 的脏页可被刷盘。

**查看 Buffer Pool 状态**：

```sql
SHOW ENGINE INNODB STATUS\G
-- 关注 BUFFER POOL AND MEMORY 段

SELECT pool_id, pool_size, free_buffers, database_pages,
       modified_db_pages, old_database_pages
FROM information_schema.INNODB_BUFFER_POOL_STATS;
```

**常见坑**：

- Buffer Pool 过小 → 频繁磁盘 IO，QPS 上不去。
- 多个 Buffer Pool Instance（`innodb_buffer_pool_instances`）减少锁竞争，大内存机器建议 8～16 个 instance。

---

### 3.2 Change Buffer（写缓冲，原 Insert Buffer）

对**非唯一二级索引**的 INSERT/UPDATE/DELETE，若索引页不在 Buffer Pool，可先写入 Change Buffer，后续合并（merge）到索引页，减少随机 IO。

```
UPDATE 二级索引列
       │
       ▼
  目标索引页在 BP？ ──Yes──► 直接修改索引页
       │
       No
       ▼
  写入 Change Buffer（内存 + 持久化到 ibdata 系统表空间）
       │
       后台 merge / 下次读该页时 merge
```

**限制**：唯一索引必须立即判重，**不能**走 Change Buffer。

**参数**：`innodb_change_buffer_max_size`（默认 25% Buffer Pool）、`innodb_change_buffering`（all/none/inserts/deletes/purges）。

---

### 3.3 Adaptive Hash Index（AHI）

InnoDB 对热点 B+ 树页建立哈希索引，等值查询可 O(1) 定位。由引擎自动维护，**不可手动创建**。

- 高并发 OLTP 等值点查可能受益。
- 高写负载下 AHI 维护有开销，极端场景可 `SET GLOBAL innodb_adaptive_hash_index=OFF` 做 A/B 验证。

---

### 3.4 Log Buffer（日志缓冲）

Redo Log 写入内存缓冲区，再按策略刷到磁盘 `ib_logfile*`。

| 参数 | 含义 | 默认 |
|------|------|------|
| `innodb_log_buffer_size` | Log Buffer 大小 | 16MB（大事务可调 64～256MB） |
| 刷盘时机 | 事务提交时 / buffer 满 1/2 / 后台线程 | 见 §9 |

---

## 4. 磁盘结构

### 4.1 Tablespace 与 .ibd 文件

| 类型 | 文件 | 说明 |
|------|------|------|
| 系统表空间 | `ibdata1` | 数据字典、Change Buffer、Undo（5.7 前部分）、Doublewrite |
| 独立表空间 | `{table}.ibd` | `innodb_file_per_table=ON`（默认），每表一文件 |
| 通用表空间 | `.ibd` | `CREATE TABLESPACE` 创建，多表共享 |
| Undo 表空间 | `undo_001`… | 8.0 独立 Undo 表空间，便于 truncate |
| 临时表空间 | `ibtmp1` | 用户临时表 |

**Java 后端关注点**：

- 删表 `DROP TABLE` 在 file_per_table 下会释放 `.ibd` 空间；系统表空间不会自动缩小。
- 大表 DDL、分区表、Transportable Tablespace 都绕不开 `.ibd` 理解。

---

### 4.2 Doublewrite Buffer（双写缓冲）

防止 **partial page write**（16KB 页刷盘只写了一半就断电，Redo 无法修复半页）。

```
脏页刷盘流程：
  Buffer Pool 脏页
       │
       ▼
  先顺序写入 Doublewrite Buffer（共享表空间固定区域，2MB 批次）
       │
       ▼
  再写入真实 .ibd 位置
       │
  崩溃恢复：若 .ibd 页损坏，从 Doublewrite 拷贝完整页覆盖
```

**代价**：额外一次顺序写；**收益**：避免数据文件不可恢复的 torn page。

`innodb_doublewrite=ON`（默认），极少数 NVMe + 原子写环境才讨论关闭。

---

## 5. Redo Log（重做日志）

### 5.1 WAL 原则

**Write-Ahead Logging**：先写日志，再写数据页。提交时不必立即刷脏页，只要 Redo Log 落盘即可在崩溃后重做。

```
事务 UPDATE
    │
    ├─► 修改 Buffer Pool 中的数据页（脏页）
    │
    └─► 写 Redo Log（物理日志：某页某偏移改成什么）
            │
            commit 成功 ← Redo Log 刷盘（策略见 §9）
```

### 5.2 文件与循环写

- 文件：`ib_logfile0`、`ib_logfile1`…（或 `#innodb_redo` 目录，8.0.30+）
- 大小：`innodb_redo_log_capacity`（8.0.30+）或 `innodb_log_file_size × 文件数`
- **循环使用**：写满后回到文件头，覆盖旧 Redo（旧记录对应脏页必须已刷盘）

### 5.3 Checkpoint

Checkpoint LSN 表示：**该 LSN 之前的 Redo 对应脏页都已刷盘**，这部分 Redo 文件空间可复用。

```
Redo Log 文件（环形）
[====已刷盘可覆盖====|====未刷盘====|==当前写入==]
        ↑ checkpoint LSN              ↑ current LSN
```

Checkpoint 过慢 → Redo 空间耗尽 → 阻塞更新（ fierce checkpoint）。

**监控**：

```sql
SHOW ENGINE INNODB STATUS\G
-- LOG 段：Log sequence number / Log flushed up to / Last checkpoint at
```

### 5.4 Crash Recovery 流程

1. 读取最新 Checkpoint LSN。
2. 从 Checkpoint 起扫描 Redo Log，**重做（redo）** 已提交事务的物理修改。
3. 利用 Undo Log **回滚** 未提交事务。
4. 数据库恢复到一致状态。

**耗时因素**：Redo 量、脏页数量、磁盘 IO。大实例异常断电后恢复可能数分钟。

---

## 6. Undo Log（回滚日志）

### 6.1 作用

| 用途 | 说明 |
|------|------|
| 事务回滚 | 保存修改前镜像，ROLLBACK 时逆操作 |
| MVCC | 旧版本链供快照读（Read View）遍历 |
| Purge | 无事务再需要旧版本时，后台清理 Undo |

### 6.2 版本链（简要）

```
聚簇索引行 ROW
  DB_TRX_ID │ DB_ROLL_PTR │ col1 │ col2 ...
            │
            └──► Undo Record (v1) ──► Undo Record (v0) ──► NULL
                  TRX_ID=102           TRX_ID=101
```

- `DB_TRX_ID`：最后修改该行的事务 ID。
- `DB_ROLL_PTR`：指向 Undo 链上一版本。
- 快照读通过 Read View 判断哪个版本可见（详见第 03 章）。

**Undo 膨胀**：长事务不提交 → Undo 无法 Purge → 表空间暴涨、`history list length` 飙高。

```sql
-- 8.0 查看长事务
SELECT * FROM information_schema.INNODB_TRX
ORDER BY trx_started;
```

---

## 7. Binlog（二进制日志）

Binlog 由 **Server 层** 产生，与引擎无关，用于**主从复制**与** point-in-time 恢复**。

### 7.1 三种格式

| 格式 | 记录内容 | 优点 | 缺点 |
|------|----------|------|------|
| STATEMENT | 原始 SQL | 日志小 | 不确定函数、触发器可能导致主从不一致 |
| ROW | 行级 before/after image | 最安全、一致性好 | 日志大（大更新爆量） |
| MIXED | 自动选择 | 折中 | 行为难预测 |

**生产推荐**：`binlog_format=ROW`，配合 `binlog_row_image=FULL`（或 MINIMAL 省空间，需评估）。

```sql
-- 查看 binlog 事件
SHOW BINLOG EVENTS IN 'binlog.000123' LIMIT 20;
mysqlbinlog --base64-output=DECODE-ROWS -v binlog.000123
```

### 7.2 sync_binlog

| 值 | 行为 | 风险 |
|----|------|------|
| 0 | OS 刷盘，性能最好 | 崩溃可能丢 binlog，主从不一致 |
| 1 | 每次 commit 刷 binlog | 最安全，IO 压力大 |
| N | 每 N 次 commit 刷一次 | 折中 |

---

## 8. Redo vs Undo vs Binlog 对比

| 维度 | Redo Log | Undo Log | Binlog |
|------|----------|----------|--------|
| 层级 | InnoDB 引擎 | InnoDB 引擎 | MySQL Server |
| 类型 | 物理日志（页级） | 逻辑逆操作 / 旧版本 | 逻辑日志（SQL 或行变更） |
| 作用 | 崩溃恢复、持久化已提交 | 回滚、MVCC | 复制、备份恢复 |
| 循环/追加 | 循环写 | 段式管理、Purge | 追加写、可 purge |
| 事务参与 | 两阶段提交 | 不参与复制协议 | 两阶段提交 |

**记忆口诀**：Redo 保**提交**（已提交不丢），Undo 保**撤销与多版本**，Binlog 保**复制与审计**。

---

## 9. 两阶段提交（Redo + Binlog）

**问题**：InnoDB 先写 Redo、Server 再写 Binlog，若只完成一半就崩溃，主从或恢复会不一致。

**解法**：内部 XA 两阶段提交，保证 Redo 与 Binlog **要么都有，要么都没有**（对应该事务）。

### 9.1 详细步骤（ROW 格式 UPDATE 为例）

```
阶段                    InnoDB                    Server (Binlog)
─────────────────────────────────────────────────────────────────
1. 执行 UPDATE          修改 BP 脏页
2. 写 Undo              写 Undo Log（持久化策略同 Redo 组）
3. 写 Redo              Redo 写入 Log Buffer
4. prepare              Redo prepare 标记刷盘 ────────────────┐
5. 写 Binlog                                      写 Binlog Buffer
6. 刷 Binlog                                        sync_binlog 刷盘
7. commit               Redo commit 标记刷盘 ◄── Binlog 已有则提交
                        （或 Binlog 写失败则回滚）
```

**崩溃恢复判定**（简化）：

| 崩溃点 | Redo | Binlog | 恢复动作 |
|--------|------|--------|----------|
| A | 无 prepare | 无 | 回滚事务 |
| B | prepare | 无 | 回滚事务 |
| C | prepare | 有 | **提交**（补写 commit） |
| D | commit | 有 | 已提交，无需处理 |

**关键**：以 **Binlog 是否存在该 XID 事务** 为仲裁，保证备库能通过 Binlog 重放，与主库 InnoDB 状态一致。

**Java 面试常问**：为什么有了 Redo 还要 Binlog？

- Redo 是 InnoDB 私有的循环物理日志，备库无法直接读 Redo 复制。
- Binlog 是 Server 层逻辑日志，跨引擎、跨版本，复制生态标准。

---

## 10. 数据页与行格式

### 10.1 Page 结构（16KB）

```
┌─────────────────────────────────────────┐
│ File Header (38B)  FIL_PAGE_OFFSET 等    │
├─────────────────────────────────────────┤
│ Page Header (56B)  n_recs, heap_no...   │
├─────────────────────────────────────────┤
│ Infimum + Supremum (伪记录)              │
├─────────────────────────────────────────┤
│ User Records (行记录，单向链表)           │
├─────────────────────────────────────────┤
│ Free Space                               │
├─────────────────────────────────────────┤
│ Page Directory (槽，二分查找)             │
├─────────────────────────────────────────┤
│ File Trailer (8B)  checksum              │
└─────────────────────────────────────────┘
```

### 10.2 行格式（ROW_FORMAT）

| 格式 | 特点 | 现状 |
|------|------|------|
| COMPACT | 紧凑，变长字段偏移 | 5.0 引入 |
| REDUNDANT | 旧格式 | 淘汰 |
| DYNAMIC | 溢出列存页外，只留 20B 指针 | **8.0 默认** |
| COMPRESSED | 压缩页 | 只读或多读少写 |

```sql
CREATE TABLE t (
  id BIGINT PRIMARY KEY,
  body TEXT
) ROW_FORMAT=DYNAMIC;
-- 大 TEXT/BLOB 溢出到 overflow page，主索引页只留指针
```

**坑**：`ROW_FORMAT=COMPACT` + 宽 varchar 可能导致页分裂频繁；统一 DYNAMIC + 合理字段长度。

---

## 11. 刷盘策略与 CAP 权衡

### 11.1 innodb_flush_log_at_trx_commit

| 值 | 行为 | TPS | 崩溃丢数据 |
|----|------|-----|------------|
| 0 | 每秒刷 Redo | 最高 | 最多丢 1 秒 |
| 1 | 每次 commit fsync Redo | 最低 | **不丢**（单实例） |
| 2 | 每次 write，每秒 fsync | 中等 | OS 崩溃可能丢 |

### 11.2 与 sync_binlog 组合

| flush_log_at_trx_commit | sync_binlog | 场景 |
|-------------------------|-------------|------|
| 1 | 1 | **金融/订单**（双 1，最安全） |
| 1 | 0 或 100 | 主库安全，复制略有延迟风险 |
| 2 | 100 | 日志/埋点（可丢少量） |

**真实故障**：双 1 下磁盘 IO 成为瓶颈，TPS 从 8k 降到 2k；换 RAID10 NVMe + 适当 `innodb_log_file_size` 后恢复。不可为性能单独把 flush 改为 0 而不评估业务容忍度。

---

## 12. 生产调优参数速查

| 参数 | 建议方向 | 说明 |
|------|----------|------|
| `innodb_buffer_pool_size` | 物理内存 60～75% | 最重要 |
| `innodb_buffer_pool_instances` | 8～16（BP ≥ 8GB） | 减 latch 竞争 |
| `innodb_log_file_size` / `innodb_redo_log_capacity` | 1～4GB | 避免 checkpoint 过频 |
| `innodb_flush_log_at_trx_commit` | 1（默认） | 按业务可协商 2 |
| `sync_binlog` | 1 或 100 | 复制一致性 vs IO |
| `innodb_io_capacity` | SSD 2000～4000 | 脏页刷盘速率 |
| `innodb_io_capacity_max` | 2× io_capacity | 峰值 |
| `innodb_max_undo_log_size` | 1GB+ | 触发 Undo truncate |
| `innodb_thread_concurrency` | 0（默认无限） | 高并发一般不改 |

**诊断 SQL**：

```sql
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool%';
SHOW GLOBAL STATUS LIKE 'Innodb_log%';
SHOW VARIABLES LIKE 'innodb_flush%';
```

---

## 13. 常见生产场景

### 场景 A：数据库重启慢

- **原因**：Crash Recovery 扫描大量 Redo；或 Buffer Pool Warmup。
- **排查**：错误日志 `InnoDB: Starting crash recovery` 到 `ready for connections` 耗时；`innodb_fast_shutdown=1` 正常关机可减少 Recovery 量。

### 场景 B：写入突然卡顿

- **原因**：Redo 写满 fierce checkpoint；磁盘 IO 饱和；双 1 + sync_binlog=1。
- **排查**：`SHOW ENGINE INNODB STATUS` → `pending writes`、`Log sequence number` 与 checkpoint 差距。

### 场景 C：Undo 表空间暴涨

- **原因**：未提交长事务、批量 DELETE 未分批。
- **处理**：杀长事务、分批删除、`innodb_purge_threads=4`。

### 场景 D：从库断链后追平

- 依赖 **Binlog + ROW**，与 Redo 无关；理解两阶段提交才能解释「主库已 commit 从库为何还查不到」（复制延迟，非日志丢失）。

---

## 14. 常见坑汇总

1. **以为 commit 就写磁盘数据页** —— 实际多数时候只刷 Redo，脏页异步刷。
2. **混淆 Redo 与 Binlog** —— 复制、PITR 只看 Binlog。
3. **长事务** —— Undo 堆积、锁持有、主从延迟三重打击。
4. **Buffer Pool 命中率低** —— `Innodb_buffer_pool_reads` / `Innodb_buffer_pool_read_requests` > 1% 需扩容或优化 SQL。
5. **关闭 doublewrite** —— 除非完全理解 torn page 风险。
6. **STATEMENT binlog + 非确定性函数** —— 主从不一致经典坑。

---

## 15. 面试 Q&A（18 题）

### Q1：InnoDB 和 MyISAM 最大区别？

**答**：InnoDB 支持事务与行级锁，用 Redo/Undo 实现崩溃恢复和 MVCC；数据按聚簇索引组织。MyISAM 无事务、表锁、崩溃易损坏，适合只读场景。生产 OLTP 选 InnoDB。

### Q2：什么是 Buffer Pool？为什么需要 LRU？

**答**：缓存磁盘数据页和索引页，减少 IO。LRU 保留热点页；InnoDB 改进为 young/old 分区，防止全表扫描一次性加载大量冷页挤掉热点。

### Q3：脏页什么时候刷盘？

**答**：Redo checkpoint 推进、Buffer Pool 空闲不足、后台 master thread 定期、Shutdown 时。**不是** commit 时立即刷脏页（WAL）。

### Q4：Redo Log 为什么循环写而 Binlog 追加？

**答**：Redo 只负责使**数据页**恢复到崩溃前已提交状态，Checkpoint 后对应 Redo 可覆盖。Binlog 供复制与备份，必须保留直到 expire 或备份消费。

### Q5：什么是 LSN？

**答**：Log Sequence Number，Redo 字节偏移单调递增标识。Flush List、Checkpoint、Recovery 都依赖 LSN 对齐。

### Q6：Doublewrite 解决什么问题？

**答**：16KB 页 partial write。先写 doublewrite 完整副本，再写数据文件；恢复时若页 checksum 失败则从 doublewrite 还原。

### Q7：Change Buffer 适用于什么索引？

**答**：**非唯一**二级索引。唯一索引需即时判重，不能延迟 merge。

### Q8：Undo Log 有哪些用途？

**答**：事务回滚、MVCC 多版本链、Purge 清理。长事务导致 Undo 无法 Purge。

### Q9：崩溃恢复时 Redo 和 Undo 各做什么？

**答**：Redo **前滚**已提交（prepare+有 binlog 或已 commit）；Undo **回滚**未提交事务，使数据一致。

### Q10：什么是两阶段提交？为什么需要？

**答**：InnoDB prepare（Redo）→ 写 Binlog → InnoDB commit。解决 Redo 与 Binlog 只写一半的不一致，以 Binlog 为事务是否提交的仲裁。

### Q11：innodb_flush_log_at_trx_commit=2 丢什么数据？

**答**：OS crash 可能丢最近 1 秒内已 commit 但未 fsync 的 Redo；MySQL 进程 crash 不丢（write 已进 OS buffer，视 OS 策略）。

### Q12：sync_binlog=0 的风险？

**答**：Binlog 可能未落盘就返回成功，主库崩溃后备库缺少事务，**复制不一致**。

### Q13：Binlog ROW 格式下 UPDATE 记录什么？

**答**：修改行的 before image 与 after image（主键定位），备库按行应用，避免 STATEMENT 不确定性。

### Q14：Checkpoint 推进慢会怎样？

**答**：Redo 空间无法复用，写 Redo 阻塞，更新 stall，表现为 periodic write latency spike。

### Q15：Adaptive Hash Index 要不要关？

**答**：默认开，自动维护。仅当 profiling 证明 latch 竞争严重且 workload 以范围查为主时，可尝试关闭。

### Q16：.ibd 文件删除表会变小吗？

**答**：`innodb_file_per_table=ON` 时 DROP TABLE 会删文件释放空间。TRUNCATE 重建表文件。DELETE 不会缩小文件。

### Q17：Log Buffer 满了会怎样？

**答**：触发 Redo 刷盘，可能阻塞新 Redo 写入，事务 commit 变慢。

### Q18：如何向面试官画 InnoDB 写入路径？

**答**：SQL → 改 BP 脏页 → 写 Undo → 写 Redo（prepare）→ 写 Binlog → fsync Binlog → Redo commit → 返回客户端；后台刷脏页 + Purge Undo。

---

## 16. 自测清单

- [ ] 能白板画出 Buffer Pool + Redo + 脏页刷盘关系
- [ ] 能逐步口述两阶段提交流程与崩溃恢复表
- [ ] 能解释双 1 与 sync_binlog 组合的业务含义
- [ ] 能区分三种日志职责而不混淆
- [ ] 遇到「重启慢 / 写卡顿 / Undo 涨」知道看哪些 STATUS

---

← [MySQL目录](./README.md) · [上一章：速查总览](./00-速查总览.md) · [下一章：索引原理与 B+ 树](./02-索引原理与B+树.md)
