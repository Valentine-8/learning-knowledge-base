# 05 · SQL 优化与 EXPLAIN

> **适用**：7 年 Java 后端 · 慢 SQL 治理 · 执行计划解读 · 线上案例复盘  
> **前置**：[02-索引原理与B+树](./02-索引原理与B+树.md)、[04-锁机制与死锁](./04-锁机制与死锁.md)  
> **后续**：[06-主从复制与高可用](./06-主从复制与高可用.md)

---

## 一、优化方法论

```
发现慢 SQL → EXPLAIN / 慢日志 → 定位 type/rows/Extra
    → 索引/SQL 改写/架构 → 验证 → 上线 → 持续监控
```

| 阶段 | 工具 |
|------|------|
| 发现 | 慢查询日志、`performance_schema`、`pt-query-digest` |
| 分析 | `EXPLAIN`、`EXPLAIN ANALYZE`（8.0.18+）、Optimizer Trace |
| 验证 | 测试库对比 rows、time；灰度 |
| 治理 | 索引规范、SQL Review、Archery 等平台 |

---

## 二、EXPLAIN 逐列详解

```sql
EXPLAIN SELECT o.id, u.name
FROM orders o
JOIN user u ON o.user_id = u.id
WHERE o.status = 1 AND o.create_time > '2025-01-01';
```

### 2.1 输出列全表

| 列 | 含义 | 优化关注点 |
|----|------|------------|
| **id** | SELECT 标识；id 相同同组，越大越先执行（子查询/UNION 例外） | 复杂 SQL 执行顺序 |
| **select_type** | SIMPLE/PRIMARY/SUBQUERY/DERIVED/UNION/Materialized 等 | DERIVED 可能物化临时表 |
| **table** | 当前访问的表或 `<derivedN>` | |
| **partitions** | 匹配的分区 | 分区裁剪是否生效 |
| **type** | **访问类型**，性能关键 | 至少 range，避免 ALL |
| **possible_keys** | 优化器**可能**选用的索引 | 候选集 |
| **key** | **实际**使用的索引 | NULL = 未走索引 |
| **key_len** | 索引使用字节数 | 联合索引用了几列 |
| **ref** | 与索引比较的列/常数 | const、func、列 |
| **rows** | 估算扫描行数 | 越小越好，非精确 |
| **filtered** | 5.7+ 按条件过滤百分比 | 越低说明回表/过滤浪费大 |
| **Extra** | 附加信息 | Using filesort/temporary 重点排查 |

### 2.2 type 性能排序（从好到差）

| type | 含义 | 示例 |
|------|------|------|
| **system** | 表仅一行（系统表） | |
| **const** | 主键/唯一索引等值，最多一行 | `WHERE id = 1` |
| **eq_ref** | JOIN 侧主键/唯一等值 | `ref` 的 JOIN 优化版 |
| **ref** | 非唯一索引等值 | `WHERE status = 1` |
| **ref_or_null** | ref + NULL 查询 | `WHERE col = 1 OR col IS NULL` |
| **range** | 索引范围 | `BETWEEN`、`<`、`IN` |
| **index** | 全索引扫描 | 比 ALL 好，仍扫整索引 |
| **ALL** | 全表扫描 | **需优化** |

**口诀**：`system > const > eq_ref > ref > range > index > ALL`

### 2.3 key 与 possible_keys

```sql
-- possible_keys 含 idx_status, idx_time；key 为 idx_time
EXPLAIN SELECT * FROM orders WHERE status = 1 AND create_time > '2025-01-01';
```

- **key=NULL** 且 possible_keys 非空：统计信息/条件导致优化器放弃索引。
- **key_len 计算**：int(4)+nullable(1) + varchar(N×字符集字节)… 用于判断联合索引最左前缀用了几列。

### 2.4 rows 与 filtered

- **rows**：基于统计信息的**预估值**，非 EXPLAIN ANALYZE 的实际值。
- **filtered**：`rows × filtered%` ≈ 与下表 JOIN 的行数估计。
- **5.7 前无 filtered**：只看 rows。

```sql
-- 8.0 真实执行
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 1;
```

### 2.5 Extra 常见值

| Extra | 含义 | 建议 |
|-------|------|------|
| **Using index** | 覆盖索引 | ✓ 优 |
| **Using index condition** | ICP 索引下推 | ✓ 通常好 |
| **Using where** | 存储引擎后 Server 层过滤 | 可能需更好索引 |
| **Using temporary** | 临时表 | GROUP BY/ DISTINCT 优化 |
| **Using filesort** | 额外排序 | 调整索引或 SQL |
| **Using join buffer** | Block Nested Loop | 8.0 hash join 或加索引 |
| **Impossible WHERE** | 条件恒假 | 检查逻辑 |
| **Select tables optimized away** | MIN/MAX 等优化 | ✓ |
| **Using MRR** | 多范围读优化 | ✓ |

---

## 三、Optimizer Trace 入门

当 EXPLAIN 与预期不符时，查看优化器决策过程。

```sql
SET optimizer_trace = 'enabled=on';
SELECT * FROM t WHERE a = 1 AND b > 10;
SELECT * FROM information_schema.OPTIMIZER_TRACE\G
SET optimizer_trace = 'enabled=off';
```

**TRACE 关键段落**：

| 段落 | 内容 |
|------|------|
| `join_preparation` | 表、条件解析 |
| `join_optimization` | 考虑 access path、索引成本 |
| `rows_estimation` | 各索引 rows 估计 |
| `considered_execution_plans` | 候选计划及 cost |
| `chosen` | 最终选择及原因 |

**成本模型**：`IO cost + CPU cost`；`innodb_stats_persistent` 影响 rows 估计准确性。

```sql
-- 更新统计信息
ANALYZE TABLE orders;
```

---

## 四、JOIN 优化

### 4.1 JOIN 类型与驱动表

```sql
EXPLAIN SELECT * FROM orders o
INNER JOIN user u ON o.user_id = u.id
WHERE o.create_time > '2025-01-01';
```

- 优化器选择**驱动表**（通常小结果集）。
- 被驱动表需在 JOIN 列上有索引 → **eq_ref/ref**。

### 4.2 Nested Loop Join（传统）

```
for each row in 驱动表:
    在被驱动表索引上 lookup
```

- 被驱动表无索引 → **ALL** + `Using join buffer` → 极慢。

### 4.3 Hash Join（8.0.18+）

```sql
-- 等值 JOIN 且无合适索引时可能选 hash join
EXPLAIN FORMAT=TREE SELECT * FROM t1 JOIN t2 ON t1.a = t2.a;
```

| 对比 | Nested Loop | Hash Join |
|------|-------------|-----------|
| 适用 | 有索引、小驱动表 | 大表等值 JOIN、无索引 |
| 内存 | 低 | 需 `join_buffer` / hash 内存 |
| Extra | Using join buffer (BNL) | 8.0 `Hash join` in TREE |

**优化原则**：
1. JOIN 列类型一致，避免隐式转换。
2. 小表驱动大表（人为 STRAIGHT_JOIN 慎用）。
3. 被驱动表 JOIN 列索引必备。

### 4.4 JOIN 顺序示例

```sql
-- 三表 JOIN：先过滤 orders 时间范围（range），再 JOIN user、product
SELECT o.id, u.name, p.title
FROM orders o
JOIN user u ON o.user_id = u.id
JOIN product p ON o.product_id = p.id
WHERE o.create_time BETWEEN '2025-01-01' AND '2025-01-31'
  AND o.status = 'PAID';
-- 索引建议：orders(create_time, status, user_id, product_id) 或 status+create_time
```

---

## 五、子查询优化

### 5.1 物化与半连接（Semi-join）

```sql
-- 旧：DEPENDENT SUBQUERY，外层每行执行子查询
SELECT * FROM orders o
WHERE user_id IN (SELECT id FROM user WHERE level = 'VIP');
```

**8.0 优化器可能**：
- **Materialization**：子查询结果物化临时表 + 索引。
- **Semi-join**：`FirstMatch`、`DuplicateWeedout`、`LooseScan` 等策略。

```sql
EXPLAIN FORMAT=TREE
SELECT * FROM orders WHERE user_id IN (SELECT id FROM user WHERE level = 'VIP');
```

### 5.2 改写为 JOIN（常用）

```sql
-- 推荐写法
SELECT o.*
FROM orders o
INNER JOIN user u ON o.user_id = u.id AND u.level = 'VIP';
```

### 5.3  correlated 子查询陷阱

```sql
-- 每行 orders 执行一次子查询
SELECT *, (SELECT COUNT(*) FROM order_item oi WHERE oi.order_id = o.id) AS cnt
FROM orders o;
-- 优化：JOIN 聚合
SELECT o.*, COALESCE(oi.cnt, 0)
FROM orders o
LEFT JOIN (SELECT order_id, COUNT(*) cnt FROM order_item GROUP BY order_id) oi
  ON o.id = oi.order_id;
```

### 5.4 EXISTS vs IN

| 场景 | 建议 |
|------|------|
| 外表小、内表大且有索引 | `EXISTS` 或 semi-join |
| 内表结果集小 | `IN` |
| NULL 语义 | `IN` 需注意 NULL 三值逻辑 |

---

## 六、COUNT 优化

### 6.1 不同 COUNT 成本

| 写法 | InnoDB 行为 |
|------|-------------|
| `COUNT(*)` | 优化器选最小二级索引或聚簇，**无行内容读取**（语义等价） |
| `COUNT(1)` | 与 COUNT(*) 类似 |
| `COUNT(pk)` | 走主键索引 |
| `COUNT(col)` | 需判断 col IS NOT NULL，可能更慢 |
| `COUNT(二级索引列)` | 走该索引 |

```sql
-- 大表精确 COUNT 慢是预期
SELECT COUNT(*) FROM orders;  -- 亿级可能数秒～数十秒
```

### 6.2 优化策略

| 策略 | 适用 |
|------|------|
| **冗余计数表** | `user.order_count` 维护 |
| **缓存** | Redis 近似 + 定时校准 |
| **WHERE 条件 count** | 必须有合适联合索引 |
| **分页估算** | `EXPLAIN` rows 估总量（不准但快） |
| **汇总表** | 按日汇总 `order_daily_stats` |

```sql
-- 带条件 count 需索引
SELECT COUNT(*) FROM orders WHERE user_id = 100 AND status = 1;
-- 索引 (user_id, status) 或 (user_id, status, id)
```

### 6.3 MyISAM vs InnoDB（面试）

- MyISAM 存行数元数据，`COUNT(*)` O(1) 但不精确事务内。
- InnoDB 需扫描索引（MVCC 可见性），无 O(1) 精确值。

---

## 七、深分页优化

### 7.1 问题

```sql
-- OFFSET 大时：扫描 offset+limit 行后丢弃
SELECT * FROM orders ORDER BY id LIMIT 1000000, 20;
-- Extra: Using filesort 或大量 rows
```

### 7.2 方案对照

| 方案 | SQL 思路 | 优点 | 缺点 |
|------|----------|------|------|
| **延迟关联** | 先查 id 再 JOIN | 减少回表 | 仍需扫 offset |
| **游标/Seek** | `WHERE id > last_id LIMIT 20` | O(limit) | 不支持随机页 |
| **覆盖索引** | 索引含 ORDER BY 列 | 减回表 | 索引设计 |
| **搜索引擎** | ES 深分页 scroll/search_after | 大数据 | 架构复杂 |
| **业务限制** | 禁止跳 500 页以后 | 简单 | 产品妥协 |

### 7.3 延迟关联

```sql
SELECT o.*
FROM orders o
INNER JOIN (
  SELECT id FROM orders ORDER BY id LIMIT 1000000, 20
) t ON o.id = t.id;
-- 子查询覆盖索引 (id) 仅扫 id，外层 20 次回表
```

### 7.4 Seek Method（推荐）

```sql
-- 第一页
SELECT * FROM orders ORDER BY id LIMIT 20;
-- 下一页（last_id = 上一页最大 id）
SELECT * FROM orders WHERE id > :last_id ORDER BY id LIMIT 20;
```

### 7.5 按时间分页

```sql
-- 复合游标
SELECT * FROM orders
WHERE (create_time, id) < (:last_time, :last_id)
ORDER BY create_time DESC, id DESC
LIMIT 20;
-- 索引 (create_time, id)
```

---

## 八、真实优化案例（12 个 Before/After）

| # | 问题 | Before 症状 | After 方案 | 收益 |
|---|------|-------------|------------|------|
| 1 | 缺联合索引 | `ALL` 500万行 + filesort | `(user_id, status, create_time)` | 2s→3ms |
| 2 | 隐式类型转换 | `phone=13800138000` 全表 | `phone='13800138000'` | 走 idx_phone |
| 3 | OR 索引失效 | `user_id=1 OR remark='gift'` ALL | UNION 各走索引 | 秒级→毫秒 |
| 4 | SELECT * | 无法覆盖索引 | 只查必要列 + 覆盖索引 | 减随机 IO |
| 5 | 深分页 | `LIMIT 5000000,20` 30s | `WHERE id > ? LIMIT 20` | 30s→5ms |
| 6 | 相关子查询 | DEPENDENT SUBQUERY | 改 JOIN / 物化 | 分钟→秒 |
| 7 | GROUP BY | temporary + filesort | `(create_time, user_id)` | 消除临时表 |
| 8 | LIKE %x | 全表扫描 | FULLTEXT 或 ES | 可用索引 |
| 9 | JOIN 无索引 | 双表 ALL 笛卡尔 | `orders.user_id` 加索引 | eq_ref |
| 10 | 统计过期 | 选错 idx_status | `ANALYZE TABLE` | rows 估算正确 |
| 11 | 大批量 DELETE | 一次 500 万行 | 分批 `LIMIT 5000` | 减锁/复制 |
| 12 | ORDER BY RAND | 全表排序 | 随机 id 范围 / random 列 | 可用索引 |

**案例 1 详解（最常见）**

```sql
-- Before: type=ALL, rows=5000000
SELECT * FROM orders WHERE user_id=123 AND status=1 ORDER BY create_time DESC LIMIT 10;
-- After
ALTER TABLE orders ADD INDEX idx_user_status_time (user_id, status, create_time DESC);
-- type=ref, rows≈50
```

**案例 5 详解（深分页）**

```sql
-- Before: 扫描 5000020 行
SELECT * FROM log ORDER BY id LIMIT 5000000, 20;
-- After: 延迟关联 或 Seek
SELECT o.* FROM log o JOIN (
  SELECT id FROM log ORDER BY id LIMIT 5000000, 20
) t ON o.id=t.id;
-- 更优: SELECT * FROM log WHERE id > 5000000 ORDER BY id LIMIT 20;
```

**案例 6 详解（子查询）**

```sql
-- Before: 外层每行触发子查询
SELECT * FROM orders WHERE user_id IN (SELECT id FROM user WHERE city='SH');
-- After
SELECT o.* FROM orders o INNER JOIN user u ON o.user_id=u.id AND u.city='SH';
```

**案例 11 详解（生产 DELETE）**

```sql
-- 循环直到 ROW_COUNT()=0，避免长事务与主从延迟
DELETE FROM log WHERE create_time < '2024-01-01' LIMIT 5000;
```

---

## 九、慢查询日志

### 9.1 开启与参数

```sql
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;           -- 秒，8.0 支持微秒
SET GLOBAL log_queries_not_using_indexes = ON;  -- 慎用，日志量大
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
```

**my.cnf**

```ini
slow_query_log = 1
long_query_time = 0.5
slow_query_log_file = /data/mysql/slow.log
log_slow_extra = 1   # 8.0.14+ 额外信息
```

### 9.2 日志片段解读

```
# Time: 2025-06-01T10:00:00.123456Z
# User@Host: app[user] @ [10.0.0.1]
# Query_time: 3.456789  Lock_time: 0.000123  Rows_sent: 20  Rows_examined: 5000000
SET timestamp=1748773200;
SELECT * FROM orders WHERE status = 1 ORDER BY id LIMIT 1000000, 20;
```

| 字段 | 含义 |
|------|------|
| Query_time | 总耗时 |
| Lock_time | 等锁时间 |
| Rows_examined | 扫描行数 |
| Rows_sent | 返回客户端行数 |

**诊断**：`Rows_examined / Rows_sent` 极大 → 缺索引或深分页。

---

## 十、pt-query-digest

Percona Toolkit 聚合慢日志，找 **Top SQL**。

```bash
# 安装后
pt-query-digest /var/log/mysql/slow.log > report.txt

# 仅看最慢 20 条
pt-query-digest --limit 20 /var/log/mysql/slow.log

# 按库过滤
pt-query-digest --filter ' $event->{db} eq "order_db"' slow.log
```

**报告关注**：

| 指标 | 含义 |
|------|------|
| Query ID | 归一化 SQL 指纹 |
| Calls | 出现次数 |
| Rps | 占总时间比 |
| V/M | 方差/均值，波动大需查偶发全表 |
| Query_time 分布 | 95%/99% 分位 |

**工作流**：慢日志 → digest → 挑 Rps 最高 → EXPLAIN → 加索引/改写 → 再 digest 对比。

---

## 十一、面试 Q&A（18 题）

### Q1：EXPLAIN 最关注哪三列？

**A**：type（至少 range）、key（是否用索引）、Extra（filesort/temporary/index）。

### Q2：rows 是精确值吗？

**A**：否，统计估算；精确用 EXPLAIN ANALYZE。

### Q3：filtered 含义？

**A**：存储引擎返回行中经 WHERE 过滤后剩余百分比估计。

### Q4：Using index 和 Using where 区别？

**A**：Using index 是覆盖索引无需回表；Using where 是 Server 层过滤（可能在回表后）。

### Q5：为什么 COUNT(*) 慢？

**A**：InnoDB 无行数缓存，需扫索引；MVCC 需可见性判断。

### Q6：深分页怎么优化？

**A**：Seek `WHERE id > ?`、延迟关联、禁止大 offset、ES。

### Q7：Hash Join 何时用？

**A**：8.0 大表等值 JOIN 且无合适索引；小表有索引仍可能 Nested Loop。

### Q8：子查询一定慢吗？

**A**：不一定；8.0 物化/semi-join 可优化； correlated 仍可能慢。

### Q9：如何强制索引？

**A**：`USE INDEX` / `FORCE INDEX`；根治靠统计信息与正确索引。

### Q10：ANALYZE TABLE 作用？

**A**：更新索引 cardinality，帮助优化器选 plan。

### Q11：慢日志 Rows_examined 很大说明什么？

**A**：扫描过多，缺索引或 SQL 需改写。

### Q12：pt-query-digest 干什么？

**A**：聚合慢日志，按总耗时/次数排序找 Top SQL。

### Q13：JOIN 小表驱动大表一定对吗？

**A**：多数情况对；优化器通常选对，异常时 STRAIGHT_JOIN 或改 SQL。

### Q14：索引下推 ICP 是什么？

**A**：5.6+ 联合索引存储引擎层先过滤再回表，Extra: Using index condition。

### Q15：SELECT * 为何不好？

**A**：无法覆盖索引、回表多、网络传输大、表结构变更易踩坑。

### Q16：OR 怎么优化？

**A**：UNION 各走索引；或改 IN；保证各分支有索引。

### Q17：EXPLAIN ANALYZE 与 EXPLAIN 区别？

**A**：ANALYZE 真执行并给实际 time/rows；EXPLAIN 只估算（8.0.18+）。

### Q18：线上加索引要注意什么？

**A**：`ALGORITHM=INPLACE, LOCK=NONE`；大表用 pt-osc；低峰；监控复制延迟。

---

## 十二、本章小结

| 工具 | 用途 |
|------|------|
| EXPLAIN | 估算计划 |
| EXPLAIN ANALYZE | 真实耗时 |
| Optimizer Trace | 优化器为何这么选 |
| slow log + pt-query-digest | 发现 Top 慢 SQL |

**7 年工程师标准**：不仅能加索引，还要能解释 **为何选错 plan**、**深分页架构方案**、**COUNT/报表架构**，并与 [06 主从](./06-主从复制与高可用.md) 读写分离、[07 分库](./07-分库分表与分布式ID.md) 联动。

---

## 导航

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [04-锁机制与死锁](./04-锁机制与死锁.md) | [MySQL README](./README.md) | [06-主从复制与高可用](./06-主从复制与高可用.md) |

↑ [数据与中间件](../../README.md)
