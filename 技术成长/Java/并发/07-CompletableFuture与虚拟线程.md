# 07 · CompletableFuture 与虚拟线程

> **目标读者**：7 年 Java 后端，能用 CompletableFuture 编排异步链路，了解 Java 21 虚拟线程适用边界与 pin 问题。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 为什么需要 CompletableFuture

`Future` 只能阻塞 `get()`，无法链式组合、无法编排多任务。

**CompletableFuture** 提供：

- 异步 supply / run
- thenApply / thenCompose 串行
- thenCombine / allOf / anyOf 并行
- exceptionally / handle 异常处理

---

## 2. 基本用法

```java
ExecutorService executor = orderPool;  // 自定义池，勿用默认

CompletableFuture<OrderDTO> future = CompletableFuture
    .supplyAsync(() -> orderClient.fetch(orderId), executor)
    .thenApply(order -> enrich(order))
    .thenCompose(order -> inventoryClient.checkAsync(order))
    .exceptionally(ex -> {
        log.warn("fallback", ex);
        return defaultOrder();
    });

OrderDTO result = future.join();  // 或 get(timeout)
```

**要点**：`supplyAsync` / `runAsync` **必须传入业务线程池**，默认 `ForkJoinPool.commonPool()` 与 `parallelStream` 争用。

---

## 3. 编排模式

### 3.1 串行

```java
.thenApply(fn)      // 同步转换，同线程可能继续
.thenApplyAsync(fn, executor)  // 下一步换线程
.thenCompose(fn)    // fn 返回 CompletableFuture，避免嵌套
```

### 3.2 并行合并

```java
CompletableFuture<String> u = fetchUser();
CompletableFuture<String> p = fetchProduct();

u.thenCombine(p, (user, product) -> merge(user, product));

CompletableFuture.allOf(f1, f2, f3).join();  // 等全部完成
CompletableFuture.anyOf(f1, f2).join();      // 任一完成
```

### 3.3 异常

```java
.handle((result, ex) -> ex != null ? fallback : result)
.exceptionally(ex -> fallback)  // 仅异常分支
.whenComplete((r, ex) -> log.info("done"))  // 不改变结果
```

---

## 4. 与线程池配合

```java
@Bean("ioExecutor")
public Executor ioExecutor() {
    return new ThreadPoolExecutor(
        32, 64, 60, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(500),
        new ThreadFactoryBuilder().setNameFormat("io-%d").build(),
        new ThreadPoolCallerRunsPolicy());
}
```

不同链路阶段可用 **同一 IO 池** 或 **分池**（查询 vs 写入）。

---

## 5. 超时控制（JDK 9+）

```java
future.orTimeout(3, TimeUnit.SECONDS)
      .completeOnTimeout(defaultVal, 3, TimeUnit.SECONDS);
```

避免 `get()` 无限阻塞。

---

## 6. 生产注意

| 坑 | 说明 |
|----|------|
| 默认线程池 | common pool 不适合 RPC/DB 阻塞任务 |
| 事务 | 异步线程无 Spring 事务 |
| 异常吞没 | `whenComplete` 不处理异常链，须 `exceptionally` |
| 嵌套 get | 用 `thenCompose` 代替 `future.get()` 阻塞 |
| 背压 | 上游无限 `supplyAsync` 仍会打满队列 |

---

## 7. 虚拟线程（Java 21+）

### 7.1 是什么

**Virtual Thread（虚拟线程）**：JVM 调度的轻量线程，挂载到少量 **载体线程**（平台/OS 线程）上。

```
大量虚拟线程 ──mount/unmount──► 少量 OS 线程（如 CPU 核数）
```

阻塞 IO 时虚拟线程 **unmount**，不占用 OS 线程 → 适合 **海量并发 IO**。

### 7.2 创建方式

```java
// 每任务一个虚拟线程
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

try (executor) {
    IntStream.range(0, 100_000).forEach(i ->
        executor.submit(() -> httpClient.get(url)));  // 可创建十万级
}

// 或直接
Thread.startVirtualThread(() -> { });
```

### 7.3 适用场景

| 适合 | 不适合 |
|------|--------|
| HTTP/RPC 客户端阻塞调用 | CPU 密集计算 |
| JDBC 阻塞查询（配合虚拟线程友好驱动） | 大量 synchronized（**pin**） |
| 高并发短 IO | native 阻塞、部分旧库 |

### 7.4 Pinning（钉住）

虚拟线程在 **synchronized 块内** 或 **native 方法** 中阻塞时，无法 unmount，占满载体线程。

**缓解**：

- 用 `ReentrantLock` 替代 synchronized
- `-Djdk.tracePinnedThreads=full` 诊断
- CPU 密集仍用平台线程池

### 7.5 与线程池对比

| | 平台线程池 | 虚拟线程 |
|--|-----------|----------|
| 线程数 | 有限（百级） | 百万级 |
| 栈内存 | MB 级/线程 | KB 级 |
| 调度 | OS | JVM |
| 适用 | CPU + 通用 | IO 密集 |

**Spring Boot 3.2+**：`spring.threads.virtual.enabled=true` 可让 Tomcat 使用虚拟线程处理请求（评估 DB 连接池、锁后再上）。

---

## 8. Structured Concurrency（预览）

JDK 21+ `StructuredTaskScope`：子任务生命周期绑定父作用域，父取消则子全取消，避免孤儿任务。逐步替代手动 `allOf`。

---

## 9. 面试题精选

**Q：CompletableFuture 和 FutureTask 区别？**  
A：CompletableFuture 支持链式、组合、异常处理；FutureTask 是 Runnable + Future 包装，能力有限。

**Q：虚拟线程会替代线程池吗？**  
A：IO 密集场景部分替代；CPU 密集、需精细隔离/限流仍用 ThreadPoolExecutor。

**Q：为什么虚拟线程不要池化？**  
A：创建成本极低，**一任务一线程** 模型更简单；池化反而限制并发度。

---

## 10. 本章小结

- CompletableFuture：**指定线程池 + thenCompose + 超时 + 异常链**。
- 虚拟线程：**IO 密集利器**，注意 synchronized pin 与连接池大小。

← [06 ThreadLocal](./06-ThreadLocal与死锁.md) · [08 面试题库](./08-生产案例与面试题库.md)
