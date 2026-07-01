# 01 · 并发基础与 happens-before

> **目标读者**：7 年 Java 后端，能讲清 JMM、三要素、线程状态与 happens-before 规则，并在面试中区分「编译优化」与「并发 bug」。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 进程、线程与并发模型

| 概念 | 说明 |
|------|------|
| **进程** | 资源分配单位，独立地址空间 |
| **线程** | CPU 调度单位，共享进程堆、方法区 |
| **并发** | 逻辑上同时处理多任务（单核时间片切换） |
| **并行** | 物理上同时执行（多核） |

Java 线程映射到 OS 线程（1:1 模型）。Java 21 **虚拟线程**是用户态轻量线程，挂载到少量载体线程（carrier thread）上。

---

## 2. 线程生命周期

```
NEW → RUNNABLE → {RUNNING}
                    ↓
         BLOCKED / WAITING / TIMED_WAITING
                    ↓
                 TERMINATED
```

| 状态 | 触发 |
|------|------|
| BLOCKED | 等待 synchronized 锁 |
| WAITING | `wait()`、`join()`、`LockSupport.park()` |
| TIMED_WAITING | 带超时的 `sleep`、`wait(timeout)` |

**`start()` vs `run()`**：`start()` 新建线程执行；直接调 `run()` 只是普通方法调用，仍在当前线程。

---

## 3. 并发三要素（面试必讲）

### 3.1 原子性

一组操作要么全部完成，要么全部不完成。`i++` 在字节码层是 **读-改-写** 三步，非原子。

**手段**：synchronized、Lock、`Atomic*` CAS。

### 3.2 可见性

每个线程有工作内存（CPU 缓存），修改可能只留在本地，其他线程读不到。

**手段**：volatile 写刷主存、读从主存；synchronized 解锁会把修改同步到主存。

### 3.3 有序性

编译器和 CPU 会 **指令重排** 优化性能，单线程结果不变，多线程可能看到「半初始化」对象。

**手段**：volatile、synchronized、happens-before 规则。

---

## 4. Java 内存模型（JMM）

JMM 定义：**什么情况下，一个线程对共享变量的写对另一个线程可见**。

```
┌──────────┐     主内存（堆）      ┌──────────┐
│ 线程 A    │ ←──── read/write ────→ │ 共享变量  │
│ 工作内存  │                        └──────────┘
└──────────┘              ↑
┌──────────┐              │
│ 线程 B    │ ←────────────┘
│ 工作内存  │
└──────────┘
```

JMM 不保证普通读写立即可见，只保证 **happens-before** 关系成立时的可见性。

---

## 5. happens-before 规则

无需逐条背诵，理解 **传递性**：A hb B，B hb C → A hb C。

| 规则 | 含义 |
|------|------|
| **程序次序** | 同一线程内，前面的操作 hb 后面的（允许重排，但 hb 语义不变） |
| **监视器锁** | 解锁 hb 后续对同锁的加锁 |
| **volatile** | volatile 写 hb 后续对同一变量的读 |
| **线程 start** | `start()` hb 新线程内任意操作 |
| **线程 join** | 新线程所有操作 hb `join()` 返回 |
| **传递性** | 链式推导 |

**经典应用**：DCL 单例中 `volatile` 禁止 `new` 指令重排，保证其他线程不会看到未构造完成的对象（见 [03 章](./03-volatile与CAS.md)）。

---

## 6. 创建线程的方式

| 方式 | 评价 |
|------|------|
| 继承 `Thread` | 不推荐，单继承限制 |
| 实现 `Runnable` | 常用，任务与线程分离 |
| 实现 `Callable` + `Future` | 可返回结果、抛异常 |
| **线程池** | **生产唯一推荐**（见 [05 章](./05-线程池ThreadPoolExecutor.md)） |
| 虚拟线程 `Executors.newVirtualThreadPerTaskExecutor()` | IO 密集新选择（见 [07 章](./07-CompletableFuture与虚拟线程.md)） |

**禁止**：生产环境 `new Thread()` 裸建线程，无法统一管理、监控、限流。

---

## 7. 并发容器 vs synchronized 集合

| 类型 | 示例 | 特点 |
|------|------|------|
| 同步包装 | `Collections.synchronizedList` | 全表锁，性能差 |
| 并发容器 | `ConcurrentHashMap`、`CopyOnWriteArrayList` | 分段/CAS/写时复制 |
| 阻塞队列 | `ArrayBlockingQueue` | 生产者-消费者 |

详见 [ConcurrentHashMap 笔记](../笔记/phase1-集合/03-ConcurrentHashMap.md)。

---

## 8. 面试题精选

**Q：为什么需要 JMM，不能直接看 CPU 缓存文档？**  
A：JMM 是 Java 语言层面的跨平台契约，屏蔽不同硬件内存模型差异，让程序员用 volatile/synchronized 就能写出正确并发程序。

**Q：单例模式 double-checked locking 为什么需要 volatile？**  
A：`new Singleton()` 可能被重排为：分配内存 → 赋值引用 → 构造。其他线程可能看到非 null 但未构造完的对象。volatile 禁止该重排。

**Q：final 字段的可见性？**  
A：正确构造后，final 字段对所有线程可见（JMM 保证），无需额外同步。

---

## 9. 本章小结

- 并发 bug 根因常落在 **三要素** 某一环缺失。
- **happens-before** 是判断可见性的工具，不是锁的替代品。
- 生产代码优先 **线程池 + 并发容器**，避免手写同步。

← [00 速查](./00-速查总览.md) · [02 synchronized](./02-synchronized与锁升级.md)
