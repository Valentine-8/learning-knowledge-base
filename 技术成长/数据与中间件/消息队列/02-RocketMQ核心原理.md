# 02 · RocketMQ 核心原理

> **目标**：掌握 RocketMQ 架构、Topic/Queue、Tag 过滤、事务消息、延迟消息、顺序消息等核心机制，理解其与 Kafka 的设计差异。

---

## 一、RocketMQ 是什么

Apache RocketMQ 是阿里开源的**分布式消息中间件**，2012 年诞生，2016 年捐赠 Apache。设计目标：

| 目标 | 实现手段 |
|------|----------|
| 高吞吐 | CommitLog 顺序写、ConsumeQueue 索引 |
| 低延迟 | 异步刷盘可选、长轮询拉取 |
| 高可用 | 主从同步、Dledger 自动选主 |
| 业务友好 | 事务消息、延迟消息、Tag 过滤、顺序消息 |

**适用场景**：电商订单、支付通知、业务解耦、分布式事务，国内互联网业务首选之一。

---

## 二、整体架构

```
                    ┌──────────────┐
                    │  NameServer  │  ← 轻量路由注册中心（无状态）
                    │  (集群)       │
                    └──────┬───────┘
                           │ 路由信息
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │ Broker-A │      │ Broker-B │      │ Broker-C │
   │ Master   │◄────►│ Master   │      │ Slave    │
   │ Slave    │ 同步  │ Slave    │      │          │
   └──────────┘      └──────────┘      └──────────┘
         ▲                 ▲
         │                 │
   ┌─────┴─────┐     ┌─────┴─────┐
   │ Producer  │     │ Consumer  │
   └───────────┘     └───────────┘
```

### 核心组件

| 组件 | 职责 |
|------|------|
| **NameServer** | 路由注册中心，Broker 注册 Topic 路由，Producer/Consumer 发现 Broker；**无状态、轻量** |
| **Broker** | 消息存储与转发，Master 可读写，Slave 只读（默认） |
| **Producer** | 消息生产者 |
| **Consumer** | 消息消费者（Push/Pull 两种模式） |
| **Topic** | 消息逻辑分类 |
| **MessageQueue** | 类似 Kafka Partition，Topic 下的队列 |

### 与 Kafka 架构对比

| | Kafka | RocketMQ |
|--|-------|----------|
| 元数据 | ZK/KRaft | NameServer |
| 存储 | 每 Partition 独立 Log | **CommitLog 统一写 + ConsumeQueue 索引** |
| 路由 | Metadata 在 Broker/Controller | NameServer 集中路由 |

---

## 三、Topic 与 MessageQueue

### 3.1 Topic

- 消息的一级分类，如 `OrderTopic`、`PaymentTopic`。
- 创建时需指定 **读写队列数**（`writeQueueNums` / `readQueueNums`），通常相等。
- 一个 Topic 分布在多个 Broker 上，每个 Broker 上有若干 MessageQueue。

```
OrderTopic (8 写队列):
  Broker-A: MQ-0, MQ-1, MQ-2, MQ-3
  Broker-B: MQ-4, MQ-5, MQ-6, MQ-7
```

### 3.2 MessageQueue

- Topic 在单个 Broker 上的**物理队列**，类比 Kafka Partition。
- **队列内有序**，队列间无序。
- 消费者负载均衡以 MessageQueue 为单位。

### 3.3 队列数量规划

| 考量 | 建议 |
|------|------|
| 并行度 | 消费者实例数 ≤ 总队列数 |
| 顺序消息 | 需要顺序的业务，队列数影响并行度（顺序与吞吐权衡） |
| 扩容 | 可动态增加 Broker 和队列，但**已有队列 ID 不变** |

---

## 四、消息模型

### 4.1 Message 结构

```java
Message {
    String topic;           // 主题
    String tags;            // 标签，用于过滤
    String keys;            // 业务 Key，用于查询和顺序路由
    byte[] body;            // 消息体
    Map<String, String> properties;  // 用户属性
}
```

| 字段 | 用途 |
|------|------|
| **topic** | 路由到哪个 Topic |
| **tags** | 消费者端 SQL92 或 Tag 过滤 |
| **keys** | 业务唯一标识；Console 按 Key 查消息；顺序消息 sharding |
| **properties** | 延迟级别 `DELAY`、事务 ID 等系统属性 |

### 4.2 Tag 与 Key

**Tag**：Topic 下的二级分类，**Broker 端过滤**，减少网络传输。

```
OrderTopic:
  Tag=CREATE   → 订单创建
  Tag=PAY      → 支付成功
  Tag=CANCEL   → 订单取消

Consumer 订阅：Topic=OrderTopic, SubExpression="PAY || CREATE"
```

**Key**：业务主键，如 `orderId=12345`。
- 发送时指定：`message.setKeys("12345")`
- 用于：消息轨迹查询、顺序消息路由（同 Key → 同 Queue）

### 4.3 消费模式

| 模式 | 说明 |
|------|------|
| **集群消费（Clustering）** | 同 Group 内 Queue 负载均衡，每条消息只被一个 Consumer 消费 |
| **广播消费（Broadcasting）** | 同 Group 内每个 Consumer 都收到全量消息 |

---

## 五、存储模型（CommitLog）

RocketMQ 最核心的设计：**所有 Topic 的消息写入同一个 CommitLog**。

```
Broker 存储目录：
  commitlog/          ← 所有消息顺序追加写（单文件 1GB，滚动）
  consumequeue/       ← 每个 Queue 的逻辑索引（固定 20 字节/条）
  index/              ← Key 索引，按 Key 查消息
  checkpoint/         ← 消费进度 checkpoint
  config/             ← 定时消息等配置
```

### 5.1 CommitLog

- 所有 Topic、所有 Queue 的消息**混合顺序写入** CommitLog。
- **顺序写盘** → 高吞吐。
- 单文件默认 1GB，写满滚动。

### 5.2 ConsumeQueue

- 每个 MessageQueue 对应一个 ConsumeQueue 文件。
- 每条索引 20 字节：`CommitLog Offset(8) + Size(4) + Tag HashCode(8)`。
- Consumer 读 ConsumeQueue 得 CommitLog 位置 → 再读 CommitLog 取完整消息。

**优势**：
- 写路径统一，无 Partition 碎片化
- ConsumeQueue 轻量，加载快

**对比 Kafka**：Kafka 每 Partition 独立 Log；RocketMQ 统一 CommitLog + 多级索引。

### 5.3 刷盘与同步

| 刷盘方式 | 配置 | 特点 |
|----------|------|------|
| **同步刷盘** | `SYNC_FLUSH` | 消息落盘才返回，可靠性高，吞吐低 |
| **异步刷盘** | `ASYNC_FLUSH` | 写入 Page Cache 即返回，吞吐高，可能丢 |

| 主从复制 | 配置 | 特点 |
|----------|------|------|
| **同步复制** | `SYNC_MASTER` | Master 等 Slave 同步完才返回 |
| **异步复制** | `ASYNC_MASTER` | Master 不等 Slave |

**生产推荐**：同步刷盘 + 同步复制（金融级）；异步刷盘 + 同步复制（一般业务平衡）。

---

## 六、Producer 发送流程

```
1. Producer 从 NameServer 拉取 Topic 路由
2. 选择 MessageQueue（默认轮询；可自定义 QueueSelector）
3. 消息序列化，写入 CommitLog（Broker 端）
4. 构建 ConsumeQueue 索引
5. 返回 SendResult（msgId, queueId, queueOffset）
```

### 6.1 发送方式

| 方式 | API | 特点 |
|------|-----|------|
| 同步发送 | `send(msg)` | 阻塞等结果，可靠 |
| 异步发送 | `send(msg, callback)` | 回调，高吞吐 |
| 单向发送 | `sendOneway(msg)` | 不等结果，可能丢 |

### 6.2 队列选择（QueueSelector）

```java
// 顺序消息：同 orderId hash 到同一 Queue
producer.send(msg, new MessageQueueSelector() {
    @Override
    public MessageQueue select(List<MessageQueue> mqs, Message msg, Object arg) {
        Long orderId = (Long) arg;
        int index = (int) (orderId % mqs.size());
        return mqs.get(index);
    }
}, orderId);
```

### 6.3 消息轨迹

- 开启 `enableMsgTrace` 后，消息写入 `_TraceTopic`。
- 可追踪：发送 → 存储 → 消费全链路。

---

## 七、Consumer 消费流程

### 7.1 Push vs Pull

| 模式 | 实现 | 说明 |
|------|------|------|
| **Push** | `DefaultMQPushConsumer` | 底层仍是 **Long Polling Pull**，Broker hold 请求 |
| **Pull** | `DefaultMQPullConsumer` | 应用主动拉，灵活控制 |

**常用 Push**：封装了 Rebalance、流控、重试。

### 7.2 消费进度（Offset）

- 消费位点存储在 Broker（集群模式）或 Consumer 本地（广播模式）。
- 路径：`consumerOffset/{group}/{topic}/{queueId}`

### 7.3 消费失败与重试

- 消费失败：`return ConsumeConcurrentlyStatus.RECONSUME_LATER`
- 消息进入 **%RETRY%+{group}** 重试 Topic
- 默认重试 16 次，延迟级别递增（10s, 30s, 1m, 2m, ... 2h）
- 超过次数进入 **%DLQ%+{group}** 死信队列

### 7.4 消费并发与顺序

| 监听器 | 说明 |
|--------|------|
| `MessageListenerConcurrently` | 多线程并发消费同一 Queue 的不同 batch |
| `MessageListenerOrderly` | **单 Queue 单线程**顺序消费，加分布式锁 |

---

## 八、Tag 过滤机制

### 8.1 Tag 过滤（常用）

```
Consumer: consumer.subscribe("OrderTopic", "PAY || CREATE");
```

- Broker 端根据 Tag HashCode 在 ConsumeQueue 索引中过滤。
- 简单高效，**不支持复杂表达式**。

### 8.2 SQL92 过滤

```
Consumer: consumer.subscribe("OrderTopic",
    MessageSelector.bySql("amount > 100 AND region = 'CN'"));
```

- 需消息 properties 中带可过滤字段。
- Broker 维护 Consumer 过滤表达式，拉取时过滤。
- **性能低于 Tag 过滤**，复杂场景可用。

### 8.3 过滤对比

| 方式 | 性能 | 灵活性 |
|------|------|--------|
| Tag | 高 | 低，预定义 Tag |
| SQL92 | 中 | 高，属性表达式 |
| 客户端过滤 | 低（全拉） | 最高 |

---

## 九、顺序消息

### 9.1 全局顺序

- Topic 只设 **1 个 MessageQueue**，单 Consumer → 全局有序。
- 吞吐极低，极少使用。

### 9.2 分区顺序（常用）

- 同 **Key**（如 orderId）路由到同一 MessageQueue。
- 该 Queue 使用 `MessageListenerOrderly` **单线程**消费。

```
orderId=100 → Queue-2 → 创建→支付→发货 顺序处理
orderId=200 → Queue-5 → 独立顺序
```

### 9.3 顺序消息注意事项

| 问题 | 处理 |
|------|------|
| 消费失败 | 会阻塞该 Queue 后续消息，需快速失败或进 DLQ |
| Rebalance | 顺序消费时 Queue 迁移可能导致短暂乱序，需优雅下线 |
| 扩容 | 新 Queue 不参与已有 Key 的路由，需规划 |

---

## 十、延迟消息

### 10.1 延迟级别

RocketMQ **不支持任意延迟时间**，只支持 **18 个固定级别**：

| Level | 延迟 | Level | 延迟 |
|-------|------|-------|------|
| 1 | 1s | 10 | 6min |
| 2 | 5s | 11 | 7min |
| 3 | 10s | 12 | 8min |
| 4 | 30s | 13 | 9min |
| 5 | 1min | 14 | 10min |
| 6 | 2min | 15 | 20min |
| 7 | 3min | 16 | 30min |
| 8 | 4min | 17 | 1h |
| 9 | 5min | 18 | 2h |

设置：`message.setDelayTimeLevel(3)` → 10s 后投递。

### 10.2 实现原理

```
1. 延迟消息先写入内部 Topic SCHEDULE_TOPIC_XXXX
2. 按 delayTimeLevel 分 Queue
3. ScheduleMessageService 定时扫描到期消息
4. 到期后重新写入目标 Topic 的 CommitLog，正常消费
```

### 10.3 定时消息（RocketMQ 5.x）

- 5.0 支持 **任意时间点** 定时消息（基于 Timer Wheel）。
- 4.x 只能用固定延迟级别。

### 10.4 使用场景

- 订单 30 分钟未支付自动取消
- 延迟重试（非消费失败重试）
- 定时提醒

---

## 十一、事务消息（核心）

RocketMQ **原生支持分布式事务消息**，是相比 Kafka 的核心业务优势之一。

### 11.1 问题背景

```
下单成功 → 发 MQ 通知库存扣减
若：DB 提交成功，MQ 发送失败 → 库存未扣
若：MQ 发送成功，DB 回滚 → 库存多扣
```

需要：**本地事务与消息发送的原子性**。

### 11.2 事务消息流程

```
┌──────────┐     1. 发送半消息      ┌──────────┐
│ Producer │ ─────────────────────► │  Broker  │
│          │     (对消费者不可见)    │          │
└────┬─────┘                        └────┬─────┘
     │                                   │
     │ 2. 执行本地事务（如写订单 DB）        │
     │                                   │
     ├──── 3a. commit ──────────────────►│ 半消息变为正常消息
     ├──── 3b. rollback ────────────────►│ 删除半消息
     │                                   │
     │ 4. 若长时间无 commit/rollback      │
     │    Broker 回查本地事务状态 ◄───────┤
     └──── 5. Producer 回查接口返回 commit/rollback
```

### 11.3 半消息（Half Message）

- 写入 CommitLog，但对 Consumer **不可见**（特殊 Topic `RMQ_SYS_TRANS_HALF_TOPIC`）。
- 等待 Producer 二次确认。

### 11.4 事务回查

- Producer 崩溃或未响应 → Broker 定时 **回查** Producer 的 `checkLocalTransaction`。
- 根据本地事务状态返回 COMMIT / ROLLBACK / UNKNOWN。
- UNKNOWN 会继续回查，直到有明确结果或超时。

### 11.5 代码骨架

```java
TransactionMQProducer producer = new TransactionMQProducer("group");
producer.setTransactionListener(new TransactionListener() {
    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        try {
            // 执行本地事务
            orderService.createOrder(...);
            return LocalTransactionState.COMMIT_MESSAGE;
        } catch (Exception e) {
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
    }

    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        // 回查：查 DB 订单是否存在
        if (orderService.exists(msg.getKeys())) {
            return LocalTransactionState.COMMIT_MESSAGE;
        }
        return LocalTransactionState.ROLLBACK_MESSAGE;
    }
});
```

### 11.6 事务消息限制

| 限制 | 说明 |
|------|------|
| 不支持延迟 | 事务消息与延迟互斥 |
| 不支持批量 | 一条一条发 |
| 回查需幂等 | 回查可能多次，本地逻辑需幂等 |
| 最终一致 | 非强一致，依赖回查兜底 |

---

## 十二、Rebalance（负载均衡）

### 12.1 触发条件

- Consumer 数量变化
- Topic 队列数变化
- Broker 上下线（路由变化）

### 12.2 分配策略

| 策略 | 说明 |
|------|------|
| 平均分配（默认） | Queue 轮流分给 Consumer |
| 环形分配 | 类似平均 |
| 机器 Room | 同机房优先 |
| 一致性 Hash | 减少迁移 |

### 12.3 Rebalance 影响

- 短暂停止消费
- Queue 迁移 → 可能重复消费 → **需幂等**
- 顺序消费时可能乱序 → 优雅下线

### 12.4 优化

- 固定 Consumer 实例数
- 增大 `heartbeatBrokerInterval`
- 消费逻辑快速完成，避免触发 rebalance 超时

---

## 十三、高可用：主从与 Dledger

### 13.1 传统主从

- Master 写，Slave 同步 CommitLog。
- Master 宕机 → **需手动切换** Slave 为 Master（旧版）。

### 13.2 Dledger 模式

- 基于 Raft 的 **自动选主**。
- 多副本（通常 3），Leader 写，Follower 同步。
- Master 宕机 → 自动选举新 Leader，**无需人工介入**。

---

## 十四、NameServer 原理

- **无状态**，节点间不通信。
- Broker 每 30s 心跳注册；NameServer 每 10s 检查 Broker 存活。
- Producer/Consumer 每 30s 拉取路由缓存。
- 可水平扩展，部署多个 NameServer，客户端配置 `;` 分隔。

**为何不用 ZK**：NameServer 轻量，只存路由，故障影响小；RocketMQ 设计哲学是 **简单可用**。

---

## 十五、生产常见问题

| 问题 | 原因 | 处理 |
|------|------|------|
| 消息堆积 | 消费慢、Consumer 少 | 扩容 Consumer、批量消费、临时跳过 |
| 消费失败进 DLQ | 业务异常、超时 | 监控 DLQ、人工/自动补偿 |
| 事务消息悬挂 | 本地事务成功但未 commit | 完善回查逻辑 |
| 顺序消息阻塞 | 一条失败卡住 Queue | 快速失败、死信 |
| 延迟不准 | 级别离散、Schedule 扫描周期 | 5.x Timer 或外部调度 |

---

## 十六、本章小结

| 概念 | 一句话 |
|------|--------|
| CommitLog | 全 Topic 统一顺序写，ConsumeQueue 为索引 |
| Tag/Key | Tag 过滤；Key 查消息与顺序路由 |
| 事务消息 | 半消息 + 本地事务 + commit/rollback + 回查 |
| 延迟消息 | 18 固定级别，Schedule Topic 定时投递 |
| 顺序消息 | 同 Key 同 Queue + Orderly 单线程消费 |
| NameServer | 轻量无状态路由中心 |

---

## 十七、消息存储文件详解

### 17.1 CommitLog 文件

```
文件命名：00000000000000000000（起始 offset）
单文件大小：默认 1GB（mappedFileSizeCommitLog）
写入方式：MappedFile 内存映射，顺序追加
```

### 17.2 ConsumeQueue 结构

```
每条 20 字节：
  Offset      8B  CommitLog 中的物理偏移
  Size        4B  消息大小
  Tag Hash    8B  Tag 字符串 hashCode
```

### 17.3 IndexFile

- 按 Key  hash 查消息
- 支持按 Key 和时间范围查询（Console 消息查询）
- 文件结构：Header + Hash Slot + Index Entry

---

## 十八、流控与保护

### 18.1 发送流控

- Broker 端 `sendMessageThreadPoolQueueCapacity` 队列满 → 拒绝或慢响应
- 快速失败保护 Broker 不被打垮

### 18.2 消费流控

```java
consumer.setPullThresholdForQueue(1000);      // 本地缓存消息数
consumer.setPullThresholdSizeForQueue(100);   // MB
consumer.setConsumeConcurrentlyMaxSpan(2000);   // 消费位点最大跨度
```

### 18.3 系统保护

- `OSPageCacheBusy`：Page Cache 使用率过高暂停写入
- 磁盘空间不足拒绝写入

---

## 十九、RocketMQ Spring 集成

```java
@RocketMQMessageListener(
    topic = "order",
    consumerGroup = "order-consumer",
    selectorExpression = "PAY || CREATE"
)
public class OrderConsumer implements RocketMQListener<OrderEvent> {
    @Override
    public void onMessage(OrderEvent event) {
        orderService.handle(event);
    }
}
```

| 注解/配置 | 说明 |
|-----------|------|
| `@RocketMQTransactionListener` | 事务消息回调 |
| `rocketmq.producer.group` | 生产者组 |
| `rocketmq.name-server` | NameServer 地址 |

---

## 二十、4.x vs 5.x 架构演进

| 特性 | 4.x | 5.x |
|------|-----|-----|
| 协议 | Remoting | Remoting + gRPC |
| 定时消息 | 18 固定级别 | 任意时间 Timer |
| 消费模式 | Push/Pull | + Pop 消费（更灵活 ack） |
| Proxy | 无 | 可选 Proxy 层，云原生 |
| 存储 | CommitLog | 可选分层存储（冷数据 offload） |

---

## 二十一、本章小结（扩展）

| 进阶主题 | 要点 |
|----------|------|
| 存储文件 | CommitLog + CQ 20B + IndexFile |
| 流控 | 发送/消费/PageCache 保护 |
| Spring | @RocketMQMessageListener、事务监听 |
| 5.x | Timer、gRPC、Pop、Proxy |

**下一章**：[03-可靠性与幂等](./03-可靠性与幂等.md)
