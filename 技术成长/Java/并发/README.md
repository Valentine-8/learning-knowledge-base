# Java 并发深度学习（JUC · 线程池 · 虚拟线程）

> **适用**：7 年 Java 后端面试 + 高并发生产排查。
> **读法**：约 12～15h；复习先看 [00-速查总览](./00-速查总览.md)。
> **速览**：Phase3 [复习手册](../笔记/phase3-并发/复习手册.md)（45 min）

---

## 章节目录

| 章 | 文档 | 核心内容 | 预计 |
|:--:|------|----------|:----:|
| 00 | [速查总览](./00-速查总览.md) | 三要素 + 线程池 7 参数 + 面试 5 分钟版 | 10 min |
| 01 | [并发基础与 happens-before](./01-并发基础与happens-before.md) | 线程模型、三要素、内存模型、JMM | 50 min |
| 02 | [synchronized 与锁升级](./02-synchronized与锁升级.md) | 对象头、偏向/轻量/重量、与 Lock 对比 | 50 min |
| 03 | [volatile 与 CAS](./03-volatile与CAS.md) | 可见性、DCL、ABA、LongAdder | 50 min |
| 04 | [AQS 与 JUC 工具](./04-AQS与JUC工具.md) | CLH 队列、Lock/Semaphore/Latch/Barrier | 60 min |
| 05 | [线程池 ThreadPoolExecutor](./05-线程池ThreadPoolExecutor.md) | 7 参数、队列选型、拒绝策略、隔离 | 60 min |
| 06 | [ThreadLocal 与死锁](./06-ThreadLocal与死锁.md) | 泄漏原理、排查、死锁四条件 | 45 min |
| 07 | [CompletableFuture 与虚拟线程](./07-CompletableFuture与虚拟线程.md) | 异步编排、Java 21 虚拟线程 | 50 min |
| 08 | [生产案例与面试题库](./08-生产案例与面试题库.md) | 故障案例、80+ 面试题 | 60 min |

---

## 配套

- JVM 内存与 GC：[笔记/phase2-JVM](../笔记/phase2-JVM/复习手册.md)
- 并发集合：[笔记/phase1-集合/ConcurrentHashMap](../笔记/phase1-集合/ConcurrentHashMap.md)
- Spring 异步陷阱：[Spring/06-事务传播与失效](../Spring/06-事务传播与失效.md)（`@Async` 与事务）
- 分布式限流：[SpringCloud/06-Sentinel](../SpringCloud/06-Sentinel与Seata.md)

← [Java 总览](../README.md)
