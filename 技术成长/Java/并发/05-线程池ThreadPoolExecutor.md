# 05 · 线程池 ThreadPoolExecutor

> **目标读者**：7 年 Java 后端，能手写线程池参数、解释执行流程、选型队列与拒绝策略，并做业务隔离与监控。
> **预计阅读**：60 min · **难度**：★★★★★

---

## 1. 为什么用线程池

| 裸建线程问题 | 线程池收益 |
|--------------|------------|
| 创建/销毁 OS 线程成本高 | 复用线程 |
| 无限创建导致 OOM | 上限可控 |
| 无法统一监控、命名 | ThreadFactory、指标 |
| 任务无队列缓冲 | 削峰、排队 |

**生产唯一推荐**：显式 `ThreadPoolExecutor`，不用 `Executors` 工厂（见下文）。

---

## 2. 七大参数

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    corePoolSize,      // 核心线程数，即使空闲也保留（除非 allowCoreThreadTimeOut）
    maximumPoolSize,   // 最大线程数
    keepAliveTime,     // 非核心线程空闲存活时间
    TimeUnit.SECONDS,
    workQueue,         // 任务队列
    threadFactory,     // 线程命名、守护线程、异常处理器
    rejectedExecutionHandler  // 拒绝策略
);
```

---

## 3. 执行流程（面试必画）

```
提交任务 execute/submit
    │
    ├─ 当前线程数 < corePoolSize → 新建核心线程执行
    │
    ├─ 否则尝试入队 workQueue
    │       │
    │       ├─ 入队成功 → 等待空闲线程
    │       └─ 队列满 → 当前线程数 < maximumPoolSize → 新建非核心线程
    │                      │
    │                      └─ 已达 max → 拒绝策略
    │
    └─ 核心线程也会从队列取任务（Worker 循环）
```

**关键**：先 **入队** 再 **扩非核心线程**（不是先扩到 max 再入队）。

---

## 4. 队列选型

| 队列 | 特点 | 场景 |
|------|------|------|
| **ArrayBlockingQueue** | 有界数组，一把 ReentrantLock | **生产推荐**，防 OOM |
| **LinkedBlockingQueue** | 链表；默认容量 ≈ `Integer.MAX_VALUE` | 注意必须显式设容量 |
| **SynchronousQueue** | 不存储，直接 handoff | `CachedThreadPool` 风格，线程数易顶 max |
| **PriorityBlockingQueue** | 优先级堆 | 定时/优先级任务 |
| **DelayQueue** | 延迟到期 | Scheduled 类任务 |

**反例**：

```java
// 危险：无界队列，任务堆积 → Full GC / OOM
Executors.newFixedThreadPool(10);  // 内部 LinkedBlockingQueue 无界

// 危险：无限线程
Executors.newCachedThreadPool();
```

---

## 5. 拒绝策略

| 策略 | 行为 | 场景 |
|------|------|------|
| **AbortPolicy**（默认） | 抛 `RejectedExecutionException` | 快速失败，调用方处理 |
| **CallerRunsPolicy** | 调用者线程执行任务 | **背压**：减慢上游 |
| **DiscardPolicy** | 静默丢弃 | 可丢的非核心任务 |
| **DiscardOldestPolicy** | 丢弃队列最老任务 | 只要最新（慎用） |

自定义：打日志 + 告警 + 降级返回。

---

## 6. 线程数如何设定

### 6.1 经验公式

**CPU 密集型**：`N + 1`（N = 核心数）  
**IO 密集型**：`2N` 或

```
线程数 ≈ CPU 核心数 × (1 + 等待时间 / 计算时间)
```

例：RT 200ms，其中 CPU 50ms → 等待/计算 = 3 → 8 核约 8×4 = 32。

### 6.2 业务隔离

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 订单线程池   │  │ 通知线程池   │  │ 查询线程池   │
│ core=20     │  │ core=5      │  │ core=50     │
└─────────────┘  └─────────────┘  └─────────────┘
```

**禁止**所有 `@Async`、RPC 回调、MQ 消费共用一个池 — 慢任务拖死快任务。

---

## 7. ThreadFactory 与命名

```java
ThreadFactory factory = new ThreadFactoryBuilder()
    .setNameFormat("order-pool-%d")
    .setUncaughtExceptionHandler((t, e) -> log.error("pool error", e))
    .build();
```

命名线程便于 **jstack**、Arthas、日志排查。

---

## 8. submit vs execute

| 方法 | 返回值 | 异常 |
|------|--------|------|
| `execute(Runnable)` | 无 | 未捕获异常 → 线程池 `afterExecute` / 默认打印 |
| `submit(Callable/Runnable)` | `Future` | 异常封装在 `Future.get()` 的 `ExecutionException` |

**生产建议**：需要结果或异常处理用 `submit` + `get`；纯 fire-and-forget 用 `execute` 并确保异常处理器。

---

## 9. 监控指标

| 指标 | 含义 |
|------|------|
| `getPoolSize()` / `getActiveCount()` | 当前/活跃线程 |
| `getQueue().size()` | 排队任务数 |
| `getCompletedTaskCount()` | 已完成 |
| 拒绝次数 | 自定义 Handler 计数 |

Micrometer + Actuator 可暴露 `executor.active` 等；队列持续满 → 扩容或降级。

---

## 10. Spring @Async 陷阱

```java
@Async("orderExecutor")  // 必须指定 Bean 名
public void sendNotify() { }
```

- 默认 `@Async` 使用 `SimpleAsyncTaskExecutor`（**每次新建线程**）或默认池，不适合生产。
- **同类内部调用** `@Async` 不生效（无代理）。
- 异步方法内 **无事务上下文**（见 Spring 事务章）。

---

## 11. ForkJoinPool 与 parallelStream

`parallelStream()` 默认使用 **common pool**（`ForkJoinPool.commonPool()`），与业务线程池 **争用 CPU**。

```java
list.parallelStream().forEach(...);  // 慎用

// 若必须用，指定自定义 ForkJoinPool 并在其内 submit
```

---

## 12. 优雅关闭

```java
executor.shutdown();  // 不再接受新任务，等队列执行完
executor.awaitTermination(60, TimeUnit.SECONDS);
// 或 shutdownNow() 中断正在执行的任务
```

Spring 容器销毁时注册 `DisposableBean` 关闭自定义池。

---

## 13. 面试题精选

**Q：core=10, max=20, 队列 100，最多多少任务在内存？**  
A：最多 20 线程 + 100 排队 = 120 个任务在处理或等待（不含已拒绝）。

**Q：CallerRunsPolicy 有什么副作用？**  
A：调用者（可能是 Tomcat 请求线程）被占用，上游吞吐下降，但起到 **背压** 保护系统。

---

## 14. 本章小结

- **有界队列 + 显式参数 + 业务隔离** 是生产三件套。
- 理解 **先入队后扩非核心** 的执行顺序。
- 拒绝策略优先理解 **CallerRuns** 的背压语义。

← [04 AQS](./04-AQS与JUC工具.md) · [06 ThreadLocal](./06-ThreadLocal与死锁.md)
