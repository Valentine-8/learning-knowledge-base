# 04 · ClickHouse 与 OLAP

## 列式存储

相同列连续存，**聚合查询**极快；不适合高频单行更新 OLTP。

## 适用

- 日志分析、BI 报表
- 宽表聚合 `GROUP BY`
- 替代 MySQL 做大数据量分析（只读/query）

## 与 MySQL

| | MySQL | ClickHouse |
|---|-------|------------|
| 模型 | 行存 OLTP | 列存 OLAP |
| 更新 | 频繁 update | 批量 insert，少 update |

## Java

JDBC 连接；或业务写 Kafka → CH 物化视图。

← [05-生产案例与面试题库](./05-生产案例与面试题库.md)
