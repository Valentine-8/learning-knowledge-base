# 04 · Kafka 与 RocketMQ 对比选型

> **目标**：从架构、功能、性能、运维、生态等维度系统对比 Kafka 与 RocketMQ，建立选型决策框架，满足 7 年工程师技术决策与面试需求。

---

## 一、选型背景

消息队列选型没有「绝对最好」，只有「最适合当前场景」。国内中大型互联网常见组合：

| 组合 | 典型场景 |
|------|----------|
| 只用 Kafka | 日志、大数据、流计算为主 |
| 只用 RocketMQ | 纯业务系统、电商、金融 |
| Kafka + RocketMQ | 日志走 Kafka，业务走 RocketMQ |
| Kafka 统一 | 业务逐步迁移 Kafka（事务 API 成熟后） |

---

## 二、架构对比

### 2.1 元数据与协调

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 元数据存储 | ZooKeeper（旧）/ KRaft（新） | NameServer |
| 复杂度 | KRaft 前需维护 ZK | NameServer 无状态，轻量 |
| Controller | 单 Controller 节点（KRaft 为 Raft 组） | Broker 内 Dledger 选主 |
| 路由发现 | Bootstrap + Metadata | NameServer 列表 |

**解读**：
- Kafka KRaft 成熟后运维简化，元数据能力更强（百万 Partition）。
- RocketMQ NameServer 设计简单，但 NameServer 全挂且 Broker 重启时路由不可用（Broker 仍有缓存）。

### 2.2 存储模型

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 模型 | 每 Partition 独立 Log | CommitLog 统一写 + ConsumeQueue |
| 顺序写 | 每 Partition 顺序写 | 全 Topic 混合顺序写 |
| 索引 | 每 Partition Offset Index | CommitLog + ConsumeQueue + Index File |
| 清理 | 按 Partition retention | CommitLog 过期删除 + CQ 联动 |

**解读**：
- Kafka 模型与 Partition 强绑定，Partition 过多时文件句柄压力大。
- RocketMQ CommitLog 写路径更集中，Topic 多时写放大更小；但读路径需两次 IO（CQ → CommitLog）。

### 2.3 复制与高可用

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 副本机制 | ISR 动态维护 | Master-Slave / Dledger Raft |
| 选主 | Controller 从 ISR 选 | Dledger 自动 / 手动切换 |
| 同步语义 | acks + min.insync.replicas | SYNC_FLUSH + SYNC_MASTER |
| 跨机房 | Rack Awareness | 同机房优先部署 |

---

## 三、功能对比

### 3.1 核心功能矩阵

| 功能 | Kafka | RocketMQ | 说明 |
|------|-------|----------|------|
| 普通消息 | ✅ | ✅ | 都支持 |
| 顺序消息 | ✅ Key+Partition | ✅ Key+Queue+Orderly | 都需同 Key 路由 |
| 延迟消息 | ⚠️ 弱（时间轮/外部） | ✅ 18 级内置 | RocketMQ 业务友好 |
| 定时消息 | ⚠️ 5.x 改进 | ✅ 5.x Timer | 新版本均支持 |
| 事务消息 | ✅ 事务 API | ✅ 半消息原生 | RocketMQ 更早成熟 |
| 消息过滤 | ⚠️ Header 过滤 | ✅ Tag / SQL92 | RocketMQ 更强 |
| 广播 | ✅ 不同 Group | ✅ Broadcasting | 都支持 |
| 消息轨迹 | ⚠️ 需自建 | ✅ 内置 Trace | RocketMQ 开箱即用 |
| 死信队列 | ❌ 需自建 | ✅ 自动 DLQ | RocketMQ 原生 |
| 消息回溯 | ✅ offset seek | ✅ 按时间/offset | 都支持 |
| 批量消息 | ✅ | ✅ | 都支持 |
| 消息压缩 | ✅ 多种算法 | ✅ | 都支持 |

### 3.2 事务能力对比

#### Kafka 事务

- 基于事务协调器 + `__transaction_state` Topic
- 适合 **Kafka 内部** Consume-Transform-Produce
- 写 DB 仍需应用层配合

#### RocketMQ 事务消息

- 半消息 + 本地事务 + 回查，**为业务分布式事务设计**
- 国内电商、支付场景验证充分
- 不支持延迟、不支持批量

**选型建议**：
- 跨 DB + MQ 业务事务 → RocketMQ 或本地消息表/Outbox
- 流处理管道 EOS → Kafka 事务

### 3.3 延迟消息对比

| | Kafka | RocketMQ |
|--|-------|----------|
| 原生支持 | 无固定级别（依赖外部或 Kafka 时间轮插件） | 18 固定延迟级别 |
| 精度 | 取决于实现 | 级别离散（1s~2h） |
| 典型方案 | Redis ZSet / 定时任务 / RocketMQ 混用 | 直接 `setDelayTimeLevel` |

---

## 四、性能对比

### 4.1 吞吐

| 场景 | Kafka | RocketMQ |
|------|-------|----------|
| 极限吞吐 | **极高**（百万级 TPS 案例多） | 高（十万级 TPS） |
| 日志采集 | 首选 | 可用但非最优 |
| 小消息高 QPS | 批量 + 零拷贝优势明显 | CommitLog 顺序写同样优秀 |

**Kafka 高吞吐原因**：
1. 顺序写 + Page Cache
2. 零拷贝 sendfile
3. Partition 并行
4. 批量与压缩

**RocketMQ** 吞吐略低于 Kafka 极限值，但对业务消息完全够用。

### 4.2 延迟

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 端到端延迟 | 毫秒级（linger.ms 影响） | 毫秒级 |
| Pull 模式 | Long Polling Fetch | Long Polling Push |
| 适合 | 吞吐优先 | 业务低延迟 + 功能 |

两者延迟均可满足业务；**Kafka linger.ms 攒批**会增大平均延迟。

### 4.3 资源消耗

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| JVM 堆 | 适中 | Broker 堆可较大（Index 缓存） |
| 磁盘 | 顺序写，友好 | 顺序写，友好 |
| 文件句柄 | Partition 多时有压力 | CommitLog 文件数少 |
| 网络 | 零拷贝优化 | 传统读写 |

---

## 五、生态对比

### 5.1 大数据生态

| 组件 | Kafka | RocketMQ |
|------|-------|----------|
| Flink | **原生深度集成** | 有 Connector |
| Spark Streaming | **原生** | 有支持 |
| Logstash/Filebeat | **首选** | 非典型 |
| ClickHouse | Kafka 引擎 | 较少 |
| Data Lake | Kafka 为主干 | 少见 |

**结论**：大数据、日志、流计算 → **Kafka 生态不可替代**。

### 5.2 业务与云生态

| 组件 | Kafka | RocketMQ |
|------|-------|----------|
| Spring | Spring Kafka | RocketMQ Spring |
| 阿里云 | 消息队列 Kafka 版 | **消息队列 RocketMQ 版**（原生） |
| 腾讯云 | CKafka | TDMQ RocketMQ |
| 微服务 | 普遍支持 | 国内 Java 栈普遍 |

### 5.3 运维与监控

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 监控 | JMX、Kafka Manager、Cruise Control | RocketMQ Console、Prometheus Exporter |
| 扩容 | 增加 Partition、Broker | 增加 Queue、Broker |
| 社区 | 全球活跃 | 国内活跃，阿里持续投入 |
| 文档 | 英文为主，丰富 | 中文资料多 |

---

## 六、开发与使用体验

### 6.1 概念映射

| 概念 | Kafka | RocketMQ |
|------|-------|----------|
| 物理分片 | Partition | MessageQueue |
| 消费组 | Consumer Group | Consumer Group |
| 位移 | Offset | Consumer Offset |
| 订阅 | Topic 订阅 | Topic + Tag/SQL |
| 路由 | Metadata | NameServer |

### 6.2 客户端

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 语言 | Java 官方 + 多语言 | Java 官方为主，多语言社区版 |
| API 风格 | 偏底层、灵活 | 业务封装多（Push、事务） |
| 学习曲线 | 需理解 Partition/ISR/Rebalance | 需理解 Tag/事务/延迟级别 |

### 6.3 常见坑

| Kafka | RocketMQ |
|-------|----------|
| Rebalance 风暴 | 延迟级别只有 18 档 |
| Partition 数规划失误 | 事务消息回查未幂等 |
| acks 配置不当丢消息 | 顺序消费失败阻塞 Queue |
| min.insync.replicas 与 acks 配合 | NameServer 全挂影响新 Producer |

---

## 七、选型决策树

```
开始
  │
  ├─ 是否大数据/日志/流计算为主？
  │     └─ 是 → Kafka
  │
  ├─ 是否需要原生事务消息、延迟消息、Tag 过滤？
  │     └─ 是 → RocketMQ（或 Kafka + 本地消息表）
  │
  ├─ 是否已有 Kafka 大数据链路，业务想统一？
  │     └─ 是 → 评估 Kafka 事务 + 幂等，逐步统一
  │
  ├─ 是否阿里云原生、国内业务文档优先？
  │     └─ 是 → RocketMQ
  │
  ├─ 极限吞吐（百万 TPS）？
  │     └─ 是 → Kafka
  │
  └─ 团队熟悉度？
        └─ 选团队精通的一种，另一种了解即可
```

---

## 八、场景推荐

### 8.1 选 Kafka

| 场景 | 理由 |
|------|------|
| 日志采集（ELK、观测） | 生态成熟 |
| 用户行为埋点 | 高吞吐、多消费者 |
| 流式 ETL | Flink/Spark 原生 |
| 事件溯源（Event Sourcing） | 持久化 + 回溯 |
| 跨数据中心复制（MirrorMaker） | 工具链完善 |

### 8.2 选 RocketMQ

| 场景 | 理由 |
|------|------|
| 电商订单流转 | 事务消息、顺序 |
| 支付结果通知 | 可靠 + 延迟（超时关单） |
| 业务解耦（Java 微服务） | API 友好、国内案例多 |
| 需要 Tag 过滤 | Broker 端过滤 |
| 需要原生 DLQ | 自动死信 |

### 8.3 混合使用

```
                    ┌─────────────┐
  业务系统 ─────────►│ RocketMQ    │──► 订单/支付/库存
                    └─────────────┘
                           │
                    Canal / 埋点
                           ▼
                    ┌─────────────┐
  日志/行为 ────────►│ Kafka       │──► Flink / ES / 数仓
                    └─────────────┘
```

**原则**：业务 MQ 与数据管道 MQ **Topic 隔离**，避免相互影响。

---

## 九、迁移考量

### 9.1 RocketMQ → Kafka

| 挑战 | 应对 |
|------|------|
| 事务消息 | 改本地消息表或 Kafka 事务 |
| 延迟消息 | 外部调度或 Redis |
| Tag 过滤 | 多 Topic 或 Header 过滤 |
| 消费 API | 重写 Consumer |

### 9.2 Kafka → RocketMQ

| 挑战 | 应对 |
|------|------|
| 大数据下游 | 保留 Kafka 管道，仅迁业务 |
| Partition 映射 | Partition → Queue 映射规划 |
| EOS 管道 | 评估 RocketMQ 是否满足 |

### 9.3 双写过渡

- 短期双写 + 对账（成本高，仅过渡期）
- 推荐：Canal/CDC 单源 + 新系统消费

---

## 十、7 年工程师面试答法

**问：你们为什么选 Kafka / RocketMQ？**

答法模板：

```
1. 场景：我们业务是 ___（电商订单 / 日志采集）
2. 需求：需要 ___（事务消息 / 百万 TPS / Flink 集成）
3. 对比：Kafka 在 ___ 更强，RocketMQ 在 ___ 更强
4. 决策：选 X，因为 ___
5. 实践：踩坑 ___，优化 ___
```

**问：两种都会吗？**

> 精通一种（能讲源码级原理 + 生产参数调优），另一种能画架构图、说清核心差异与选型边界。

---

## 十一、其他 MQ 简要对比

| MQ | 特点 | 适用 |
|----|------|------|
| **RabbitMQ** | Erlang、AMQP、路由灵活、吞吐较低 | 中小规模、复杂路由 |
| **Pulsar** | 存算分离、BookKeeper、多租户 | 云原生、跨地域 |
| **Redis Stream** | 轻量、内存 | 简单队列、低延迟小流量 |

**7 年 Java 工程师**：Kafka + RocketMQ 覆盖国内 90% 面试与工作场景；RabbitMQ 了解即可；Pulsar 作为加分项。

---

## 十二、本章小结

| 维度 | Kafka 优势 | RocketMQ 优势 |
|------|------------|---------------|
| 吞吐 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 大数据生态 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 事务/延迟/Tag | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 运维成熟度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 国内业务案例 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**下一章**：[05-面试题库与案例](./05-面试题库与案例.md)
