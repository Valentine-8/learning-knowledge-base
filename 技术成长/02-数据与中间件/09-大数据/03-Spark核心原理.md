# 03 · Spark 核心原理

## 是什么

内存计算框架，**批处理**为主，Structured Streaming 支持流。

## 核心

| 概念 | 说明 |
|------|------|
| RDD | 弹性分布式数据集（旧 API） |
| DataFrame/Dataset | 结构化 API（推荐） |
| DAG | 逻辑计划 → Stage 划分 |
| Shuffle | 宽依赖，网络开销大 |

## 调优方向

- 减少 Shuffle
- 合理 partition 数
- 广播小表 join

## 场景

离线 ETL、T+1 报表、大规模日志聚合。

← [04-ClickHouse与OLAP](./04-ClickHouse与OLAP.md)
