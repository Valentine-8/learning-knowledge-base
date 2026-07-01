# Java 分布式深度学习（CAP · 事务 · 治理 · ZK）

> **适用**：7 年 Java 后端面试 + 微服务架构设计。
> **读法**：约 10～12h；复习先看 [00-速查总览](./00-速查总览.md)。
> **速览**：Phase6 [复习手册](../笔记/phase6-分布式/00-复习手册.md)（45 min）

---

## 章节目录

| 章 | 文档 | 核心内容 | 预计 |
|:--:|------|----------|:----:|
| 00 | [速查总览](./00-速查总览.md) | CAP/BASE + 事务选型 + 面试 5 分钟版 | 10 min |
| 01 | [CAP 与 BASE](./01-CAP与BASE.md) | 定理、CP/AP 代表、最终一致 | 45 min |
| 02 | [分布式事务方案](./02-分布式事务方案.md) | 2PC/TCC/Saga/Seata/本地消息表 | 60 min |
| 03 | [分布式锁与分布式 ID](./03-分布式锁与分布式ID.md) | 选型、雪花、号段；Redis 详见专题 | 50 min |
| 04 | [限流熔断降级](./04-限流熔断降级.md) | 令牌桶、Sentinel、Hystrix | 50 min |
| 05 | [服务治理与灰度](./05-服务治理与灰度.md) | 注册发现、负载均衡、灰度路由 | 50 min |
| 06 | [ZooKeeper 与注册中心](./06-ZooKeeper与注册中心.md) | ZAB、节点类型、Curator、对比 Nacos | 60 min |
| 07 | [生产案例与面试题库](./07-生产案例与面试题库.md) | 故障案例、70+ 面试题 | 60 min |

---

## 相关专题（不重复，请跳转）

| 主题 | 文档 |
|------|------|
| **消息队列**（Kafka/RocketMQ、可靠性、幂等） | [数据与中间件/消息队列](../../02-数据与中间件/04-消息队列/README.md) |
| **Redis 分布式锁**（SET NX、Redisson、看门狗） | [Redis/04-分布式锁](../../02-数据与中间件/03-Redis/04-分布式锁与并发.md) |
| **Seata / Sentinel 实战** | [SpringCloud/06](../05-SpringCloud/06-Sentinel与Seata.md) |
| **Nacos 注册与配置** | [SpringCloud/02～03](../05-SpringCloud/02-Nacos注册发现.md) |
| **Elasticsearch** | Phase6 复习手册简述；搜索场景见架构章 |

← [Java 总览](../README.md)
