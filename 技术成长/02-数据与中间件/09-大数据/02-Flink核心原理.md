# 02 · Flink 核心原理

## 是什么

Apache Flink：**流处理优先**，批是流的特例；低延迟、Exactly-once（配合 Checkpoint）。

## 核心概念

| 概念 | 说明 |
|------|------|
| DataStream | 无界流 |
| Operator | map/filter/keyBy/window |
| Window | 滚动、滑动、会话 |
| State | Keyed State，容错 |
| Checkpoint | 分布式快照，故障恢复 |

## 与 Kafka

```
Kafka Source → Flink 计算 → Kafka/03-Redis/JDBC Sink
```

## 面试

- Flink 和 Spark Streaming 区别？（真流 vs 微批）
- Checkpoint 和 Savepoint？
- 背压是什么？

← [03-Spark核心原理](./03-Spark核心原理.md)
