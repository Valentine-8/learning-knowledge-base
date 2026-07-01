# 01 · Kafka 核心原理

> **目标**：理解 Kafka 架构、分区与副本机制、消费者组与 Rebalance、零拷贝等底层原理，能应对 7 年工程师深度面试。

---

## 一、Kafka 是什么

Apache Kafka 是一个**分布式流处理平台**，最初由 LinkedIn 开发，现已成为大数据生态的核心组件。它同时具备：

| 角色 | 说明 |
|------|------|
| 消息队列 | 异步解耦、削峰填谷 |
| 存储系统 | 消息持久化，可回溯 |
| 流处理平台 | Kafka Streams、与 Flink/Spark 集成 |

**设计哲学**：以**顺序写磁盘 + 分区并行 + 零拷贝**换取极致吞吐，牺牲部分功能灵活性（如原生事务消息、延迟消息）。

---

## 二、整体架构

```
                    ┌─────────────┐
                    │  ZooKeeper  │  （KRaft 模式后可选）
                    │  / KRaft    │
                    └──────┬──────┘
                           │ 元数据、Controller 选举
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │ Broker 0 │      │ Broker 1 │      │ Broker 2 │
   │          │      │          │      │          │
   │ Topic-A  │      │ Topic-A  │      │ Topic-B  │
   │ P0(Leader)│     │ P1(Leader)│     │ P0(Leader)│
   │ P1(Follower)│   │ P0(Follower)│   │ ...      │
   └──────────┘      └──────────┘      └──────────┘
         ▲                 ▲
         │                 │
   ┌─────┴─────┐     ┌─────┴─────┐
   │ Producer  │     │ Consumer  │
   │           │     │  Group    │
   └───────────┘     └───────────┘
```

### 核心组件

| 组件 | 职责 |
|------|------|
| **Broker** | Kafka 服务节点，存储消息、处理读写请求 |
| **Topic** | 逻辑消息分类，物理上由多个 Partition 组成 |
| **Partition** | 分区，Kafka 并行与有序的基本单位 |
| **Replica** | 分区副本，保证高可用 |
| **Producer** | 消息生产者 |
| **Consumer / Consumer Group** | 消费者及消费者组 |
| **Controller** | 集群中负责分区 Leader 选举、ISR 变更等 |
| **ZooKeeper / KRaft** | 存储集群元数据（KRaft 自 3.x 起替代 ZK） |

---

## 三、Topic 与 Partition

### 3.1 基本概念

- **Topic**：业务上的消息类别，如 `order-events`、`user-behavior-log`。
- **Partition**：Topic 的物理分片。每条消息写入某个 Partition，**分区内严格有序**，**分区间无序**。
- **Partition 数量**决定：
  - 最大并行消费数（Consumer Group 内，一个 Partition 同一时刻只能被一个 Consumer 消费）
  - 写入吞吐上限（多 Partition 可并行写）

### 3.2 消息在 Partition 内的结构

```
Partition 0:  [msg0][msg1][msg2][msg3]...
              offset=0  1     2     3

每条消息包含：
- offset：分区内单调递增的唯一编号（由 Broker 分配）
- timestamp：创建时间
- key：可选，用于分区路由
- value：消息体
- headers：可选元数据
```

### 3.3 分区策略（Producer 端）

| 策略 | 行为 |
|------|------|
| 指定 Partition | `producerRecord(topic, partition, key, value)` |
| 有 Key | `hash(key) % partitionNum`，同 Key 进同分区 → **保证 Key 级顺序** |
| 无 Key | 轮询（Sticky Partitioner 2.4+ 减少小 batch） |
| 自定义 | 实现 `Partitioner` 接口 |

**顺序消息关键**：同一业务实体（如 orderId）使用相同 Key，路由到同一 Partition。

### 3.4 Partition 数量规划

| 考量 | 建议 |
|------|------|
| 吞吐 | 分区数 ≈ 目标峰值 TPS / 单分区吞吐 |
| 消费者 | 消费者数 ≤ 分区数，否则有空闲消费者 |
| 文件句柄 | 每分区每副本在 Broker 上产生 log 文件，过多影响性能 |
| 变更成本 | 增加分区容易；**减少分区几乎不可行**（需重新分配） |

经验值：起步 6~12 个分区，按监控逐步扩容；日志类 Topic 可 32~128+。

---

## 四、副本与 ISR

### 4.1 副本机制

每个 Partition 有 **1 个 Leader + N 个 Follower**（`replication.factor` 配置，通常 3）。

| 角色 | 职责 |
|------|------|
| **Leader** | 处理该 Partition 的所有读写请求 |
| **Follower** | 从 Leader 拉取数据，不直接对外服务 |

Producer 和 Consumer 只与 **Leader** 交互（Follower 仅同步）。

### 4.2 ISR（In-Sync Replicas）

**ISR** = 与 Leader **保持同步**的副本集合（含 Leader 自身）。

Follower 被纳入 ISR 的条件（可配置）：
- `replica.lag.time.max.ms`：Follower 落后 Leader 超过该时间 → 踢出 ISR
- 旧版本用 `replica.lag.max.messages`（消息条数差）

```
Partition 0:
  Leader: Broker-1
  ISR: {Broker-1, Broker-2, Broker-3}
  非 ISR: {Broker-4}  ← 落后太多，不参与选举优先候选
```

### 4.3 ack 与持久化保证

Producer 配置 `acks`：

| acks | 含义 | 可靠性 | 延迟 |
|------|------|--------|------|
| **0** | 不等待 Broker 确认 | 最低，可能丢 | 最低 |
| **1** | Leader 写入本地 log 即返回 | Leader 宕机可能丢未同步数据 | 中等 |
| **all / -1** | ISR 中所有副本都确认 | 最高（配合 `min.insync.replicas`） | 最高 |

**`min.insync.replicas`**（Broker 端）：当 acks=all 时，ISR 副本数低于此值 → Producer 写入失败，防止「只剩 Leader 一个副本」时误报成功。

### 4.4 Leader 选举

Controller 负责选举：

1. **Preferred Leader Election**：优先将 Leader 设在 `replica.assignments` 的第一个副本（rack 感知）
2. **Unclean Leader Election**（`unclean.leader.election.enable`）：
   - **false**（推荐）：只从 ISR 中选 Leader，可能暂时不可用，但不丢已 ack 数据
   - **true**：可从非 ISR 选 Leader，可能**丢数据**，但可用性高

### 4.5 HW 与 LEO

| 术语 | 全称 | 含义 |
|------|------|------|
| **LEO** | Log End Offset | 副本最后一条消息的 offset + 1 |
| **HW** | High Watermark | 消费者可见的最大 offset（ISR 中最慢副本的 LEO） |

Consumer 只能消费 **HW 之前**的消息，保证即使 Leader 切换也不会读到未同步完的数据。

```
Leader:  LEO=10, HW=8  （Follower 最慢 LEO=8）
Follower: LEO=8
→ Consumer 最多读到 offset=7
```

---

## 五、Offset 与消费者位移

### 5.1 什么是 Offset

- **Partition 内**每条消息的唯一递增编号，从 0 开始。
- **Consumer Offset**：消费者组在某 Partition 上「已消费到哪里」的标记。

### 5.2 Offset 存储

| 版本/模式 | 存储位置 |
|-----------|----------|
| 旧版 | ZooKeeper（已废弃，性能差） |
| 现行 | 内部 Topic `__consumer_offsets`（50 个分区，Key=group+topic+partition） |

### 5.3 提交方式

| 方式 | 配置 | 特点 |
|------|------|------|
| **自动提交** | `enable.auto.commit=true` | 定时提交，可能丢消息或重复消费 |
| **手动同步** | `commitSync()` | 阻塞，精确控制 |
| **手动异步** | `commitAsync()` | 非阻塞，可能提交失败 |
| **精确一次** | 事务 + `sendOffsetsToTransaction` | EOS 场景 |

**最佳实践**：业务处理完成后再提交 offset（手动 commit），配合幂等。

### 5.4 位移重置

| 场景 | 方法 |
|------|------|
| 新消费组 | `auto.offset.reset=earliest/latest` |
| 回溯消费 | `seek(partition, offset)` |
| 跳过积压 | 重置到最新 offset（需评估业务） |

---

## 六、Consumer Group 与 Rebalance

### 6.1 Consumer Group

- 组内消费者**共同消费**一个或多个 Topic。
- **一条 Partition 同一时刻只能分配给组内一个 Consumer**。
- 不同 Consumer Group 互不影响（各自维护 offset）→ 实现**广播**。

```
Topic order (3 partitions):
  Group-A: Consumer-1 → P0, P1
           Consumer-2 → P2
  Group-B: Consumer-1 → P0, P1, P2  （独立 offset）
```

### 6.2 分区分配策略

| 策略 | 说明 |
|------|------|
| **Range** | 按 Topic 维度分配，可能不均匀 |
| **RoundRobin** | 所有 Partition 轮询，较均匀 |
| **Sticky** | 尽量保持原有分配，减少 Rebalance 代价 |
| **Cooperative Sticky** | 增量 Rebalance，不停止全部消费 |

配置：`partition.assignment.strategy`

### 6.3 Rebalance 触发条件

1. 组内 Consumer **数量变化**（上线/下线/崩溃）
2. 订阅 Topic **分区数变化**
3. 订阅 Topic **列表变化**
4. Consumer **心跳超时**（`session.timeout.ms`、`max.poll.interval.ms`）

### 6.4 Rebalance 过程

```
1. 所有 Consumer 停止消费（Stop The World）
2. 向 Coordinator 发送 JoinGroup
3. Leader Consumer 执行分区分配
4. 各 Consumer 同步分配结果
5. 开始消费
```

**问题**：Rebalance 期间**不能消费**，频繁 Rebalance 导致消费延迟、重复消费。

### 6.5 Rebalance 优化

| 手段 | 说明 |
|------|------|
| 增大 `session.timeout.ms` | 减少误判下线，但故障发现变慢 |
| 增大 `max.poll.interval.ms` | 允许更长业务处理时间 |
| 减少 Consumer 数量波动 | 固定实例数，优雅下线 |
| Cooperative Rebalance | 只迁移必要分区，减少 STW |
| 静态成员 `group.instance.id` | 重启不触发 Rebalance（2.3+） |

### 6.6 max.poll.interval.ms 与消息处理

若单条消息处理时间 × `max.poll.records` > `max.poll.interval.ms`，Consumer 会被踢出组 → Rebalance。

**解决**：
- 减小 `max.poll.records`
- 增大 `max.poll.interval.ms`
- 异步处理 + 手动 pause/resume

---

## 七、存储层原理

### 7.1 Log Segment

Partition 在磁盘上是一个目录，切分为多个 **Segment** 文件：

```
/kafka-logs/order-0/
  00000000000000000000.log    ← 消息数据
  00000000000000000000.index  ← offset → 物理位置
  00000000000000000000.timeindex
  00000000000000000001.log
  ...
```

- `log.segment.bytes`：单 Segment 大小（默认 1GB）
- `log.retention.hours/bytes`：保留策略

### 7.2 顺序写盘

Kafka 追加写 Segment 末尾 → **顺序 I/O**，接近内存速度（OS Page Cache）。

**为什么 Kafka 用磁盘还能高吞吐**：
1. 顺序写，非随机写
2. 充分利用 OS Page Cache
3. 批量读写（Producer batch、Consumer fetch）
4. 零拷贝（见下节）
5. 分区并行

### 7.3 Index 索引

- **Sparse Index**：不每条消息建索引，每隔若干字节一条 → 内存占用小
- 查找：offset → Index 二分 → .log 文件 scan

---

## 八、零拷贝（Zero Copy）

### 8.1 传统四次拷贝

Consumer 通过 Socket 从 Broker 读消息：

```
磁盘 → 内核缓冲区 → 用户缓冲区 → Socket 缓冲区 → 网卡
      (DMA)        (CPU copy)     (CPU copy)
```

4 次拷贝，2 次 CPU 参与。

### 8.2 sendfile 零拷贝

Kafka 使用 Linux `sendfile()`：

```
磁盘 → 内核 Page Cache → 直接 DMA 到网卡
```

**2 次拷贝，0 次 CPU 拷贝**（数据不经过用户空间）。

Java 实现：`FileChannel.transferTo()` → 底层 sendfile。

### 8.3 批量与压缩

- Producer：`batch.size`、`linger.ms` 攒批后一次发送
- Broker：批量写入 Segment
- 压缩：`compression.type=lz4/snappy/zstd`，降低网络与磁盘 I/O

---

## 九、Producer 核心流程

```
1. Serializer 序列化 Key/Value
2. Partitioner 选择分区
3. RecordAccumulator 按 Partition 攒批
4. Sender 线程发送 batch 到对应 Broker Leader
5. 等待 ack（按 acks 配置）
6. 失败重试（retries、retry.backoff.ms）
7. 回调 Callback
```

### 关键配置

| 配置 | 说明 |
|------|------|
| `bootstrap.servers` | Broker 地址 |
| `key.serializer / value.serializer` | 序列化 |
| `acks` | 0/1/all |
| `retries` | 重试次数 |
| `enable.idempotence` | 幂等 Producer（PID + Sequence Number） |
| `transactional.id` | 事务 Producer |

### 幂等 Producer

- Broker 为每个 Producer 分配 **PID**（Producer ID）
- 每条消息带 **Sequence Number**（分区内单调递增）
- Broker 去重：相同 PID + Partition + Seq 的重复写入被忽略

**限制**：单 Partition 内有序、防重复；**不跨 Partition、不跨 Session**（PID 随 Producer 重启变化）。

---

## 十、Consumer 核心流程

```
1. join Consumer Group
2. 分配 Partition（Rebalance）
3. fetch 请求从 Leader 拉取 batch
4. 反序列化
5. 业务处理
6. 提交 offset
```

### Fetch 机制

- `fetch.min.bytes`：最小拉取字节数
- `fetch.max.wait.ms`：不足 min.bytes 时最长等待
- **Long Polling**：Broker 无足够数据时 hold 请求，有数据再返回 → 降低空轮询

---

## 十一、Kafka 事务与 Exactly-Once

### 11.1 事务 Producer

```
transactional.id = "my-tx-producer"
initTransactions()
beginTransaction()
  send(...)
  sendOffsetsToTransaction(offsets, groupId)
commitTransaction() / abortTransaction()
```

### 11.2 事务协调器

- 内部 Topic `__transaction_state` 记录事务状态
- **Commit Marker** 写入各 Partition → Consumer 只读已提交消息

### 11.3 EOS 场景

- **Consume-Transform-Produce**：读 Kafka → 处理 → 写 Kafka，端到端精确一次
- 需：`read_committed` 隔离级别、事务 Producer、Consumer 配合

---

## 十二、KRaft 模式（简述）

Kafka 3.3+ 起 KRaft（Kafka Raft）可完全替代 ZooKeeper：

| 对比 | ZK 模式 | KRaft |
|------|---------|-------|
| 元数据 | ZK 存储 | Kafka 内部 Raft  quorum |
| 分区数上限 | 约十万级 | 百万级 |
| 运维 | 需维护 ZK 集群 | 简化 |

---

## 十三、生产常见问题

| 问题 | 原因 | 处理 |
|------|------|------|
| 消费延迟 | 消费慢、Rebalance 频繁、分区少 | 扩容分区/消费者、优化业务、Cooperative Rebalance |
| 消息乱序 | 多 Partition、重试 | 同 Key 同分区、单线程消费 |
| 磁盘满 | retention 过长、无清理 | 调整 retention、监控 disk |
| 副本不同步 | 网络、Broker 负载 | 检查 ISR、Broker 资源 |
| Rebalance 风暴 | 频繁重启、处理超时 | 静态成员、调大 timeout |

---

## 十四、本章小结

| 概念 | 一句话 |
|------|--------|
| Partition | 并行与有序单元，分区内有序 |
| ISR | 同步副本集，决定 ack=all 语义 |
| Offset | 分区内消息编号 + 消费位移 |
| Rebalance | 消费者组分区重分配，期间 STW |
| 零拷贝 | sendfile 减少 CPU 拷贝，提升吞吐 |
| HW/LEO | 控制消费可见性与副本一致性 |

---

## 十五、Consumer Coordinator 与 Group 协调

### 15.1 Coordinator 选举

- 每个 Consumer Group 对应一个 **Group Coordinator**（某 Broker 担任）
- `groupId` hash 到 `__consumer_offsets` 的某个分区 → 该分区 Leader 所在 Broker 即为 Coordinator
- Consumer 启动时 `FindCoordinator` 请求找到 Coordinator

### 15.2 JoinGroup 与 SyncGroup

```
Consumer-A ──JoinGroup──► Coordinator
Consumer-B ──JoinGroup──► Coordinator
                │
                ▼
         选 Consumer Leader（组内第一个 Join 的）
                │
Consumer Leader 计算分区分配方案
                │
         SyncGroup 广播分配结果
                │
         各 Consumer 开始 fetch
```

### 15.3 Heartbeat 机制

- Consumer 定期 `Heartbeat` 告知 Coordinator 存活
- 超时未心跳 → 认为下线 → 触发 Rebalance
- `heartbeat.interval.ms`（默认 3s）应小于 `session.timeout.ms`（默认 45s）

---

## 十六、日志压缩（Log Compaction）

### 16.1 适用场景

- **变更日志（Changelog）**：只关心 Key 最新值，如用户 profile、配置
- 相同 Key 的旧消息可被清理，保留最新

### 16.2 原理

```
log.cleanup.policy=compact

Key=user:100  offset=0  value={name: "张三"}
Key=user:100  offset=5  value={name: "张三三"}  ← 保留
Key=user:200  offset=3  value={name: "李四"}
```

- 后台 **Cleaner** 线程扫描，保留每个 Key 最新 offset，删除旧记录
- 与 delete retention 可组合：`compact,delete`

---

## 十七、MirrorMaker 与跨集群复制

### 17.1 场景

- 跨机房灾备
- 聚合多集群数据到中心集群
- 云迁移

### 17.2 MirrorMaker 2（MM2）

```
Source Cluster ──MM2 Connector──► Target Cluster
```

- 复制 Topic、Consumer Offset（可选）
- 基于 Kafka Connect 框架
- 配置：`source.cluster.alias`、`target.cluster.alias`

---

## 十八、性能调优参数速查

### Producer

| 参数 | 默认 | 调优方向 |
|------|------|----------|
| batch.size | 16KB | 增大至 32~64KB 提吞吐 |
| linger.ms | 0 | 5~20ms 攒批 |
| compression.type | none | lz4 或 zstd |
| buffer.memory | 32MB | 高吞吐增大 |

### Consumer

| 参数 | 默认 | 调优方向 |
|------|------|----------|
| fetch.min.bytes | 1 | 增大减少请求数 |
| fetch.max.wait.ms | 500 | 配合 min.bytes |
| max.poll.records | 500 | 按业务处理速度调整 |

### Broker

| 参数 | 说明 |
|------|------|
| num.network.threads | 网络线程 |
| num.io.threads | 磁盘 I/O 线程 |
| log.retention.hours | 消息保留时间 |
| log.segment.bytes | Segment 大小 |

---

## 十九、与 Spring Kafka 集成要点

```java
@KafkaListener(topics = "order", groupId = "order-group")
public void consume(ConsumerRecord<String, String> record, Acknowledgment ack) {
    try {
        orderService.process(record.value());
        ack.acknowledge();  // 手动提交
    } catch (Exception e) {
        // 不 ack，或进 DLQ
    }
}
```

| 配置 | 说明 |
|------|------|
| `enable-auto-commit=false` | 手动 ack |
| `ack-mode=MANUAL_IMMEDIATE` | 立即提交 |
| `concurrency` | 并发线程数 ≤ 分区数 |
| `retry` + `@RetryableTopic` | Spring 重试 + DLT |

---

## 二十、本章小结（扩展）

| 进阶主题 | 要点 |
|----------|------|
| Coordinator | Group 协调、Join/Sync、心跳 |
| Log Compaction | Key 最新值保留，Changelog 场景 |
| MirrorMaker | 跨集群复制 |
| 调优 | batch、linger、compression、fetch |
| Spring Kafka | 手动 ack、并发、RetryableTopic |

**下一章**：[02-RocketMQ 核心原理](./02-RocketMQ核心原理.md)
