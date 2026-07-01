# 06 · ThreadLocal 与死锁

> **目标读者**：7 年 Java 后端，能讲清 ThreadLocal 原理、线程池泄漏场景，并排查死锁与制定规避策略。
> **预计阅读**：45 min · **难度**：★★★★

---

## 1. ThreadLocal 是什么

**线程本地变量**：每个线程持有独立副本，互不干扰。

```java
private static final ThreadLocal<UserContext> CTX = new ThreadLocal<>();

public void handle() {
    CTX.set(loadUser());
    try {
        service.process();  // 下游任意层 CTX.get()
    } finally {
        CTX.remove();       // 必须清理
    }
}
```

**典型用途**：用户上下文、TraceId、SimpleDateFormat（非线程安全时的 per-thread 实例）、Spring 事务同步资源绑定。

---

## 2. 底层结构

每个 `Thread` 有 `ThreadLocalMap threadLocals`：

```
Thread
  └── ThreadLocalMap (Entry[])
         Entry: WeakReference<ThreadLocal> key → value (强引用)
```

- **key** 是弱引用 ThreadLocal 对象
- **value** 是强引用

---

## 3. 内存泄漏原理

```
ThreadLocal 对象被 GC（key 弱引用失效）
    → Entry.key = null
    → value 仍被 Entry 强引用
    → 线程存活则 value 无法回收
```

**线程池场景**：Worker 线程 **长期存活、复用**，若只 `set` 不 `remove`，value 累积 → **内存泄漏**。

**规范**：

```java
try {
    threadLocal.set(x);
    // business
} finally {
    threadLocal.remove();  // 线程池场景必做
}
```

**InheritableThreadLocal**：子线程继承父线程值；线程池下子线程复用同样需清理。异步传递上下文推荐 **TransmittableThreadLocal（TTL）** 或显式参数传递。

---

## 4. ThreadLocal 与 Spring

Spring 用 `ThreadLocal` 绑定：

- `TransactionSynchronizationManager` — 当前事务连接
- `RequestContextHolder` — 当前 HTTP 请求

这些由框架在请求结束清理；**业务自定义 ThreadLocal** 须自己 `remove()`。

---

## 5. 死锁：四个必要条件

| 条件 | 含义 |
|------|------|
| **互斥** | 资源独占 |
| **占有且等待** | 持有一锁又等另一锁 |
| **不可抢占** | 不能强行剥夺 |
| **循环等待** | A 等 B，B 等 A（或更长环） |

四者 **同时成立** 才死锁；破坏任一即可避免。

---

## 6. 经典死锁示例

```java
Object lockA = new Object();
Object lockB = new Object();

// 线程 1
synchronized (lockA) {
    synchronized (lockB) { }

// 线程 2
synchronized (lockB) {
    synchronized (lockA) { }  // 循环等待
}
```

数据库、分布式锁同样存在 **加锁顺序不一致** 问题。

---

## 7. 排查死锁

### 7.1 jstack

```bash
jstack <pid> > thread.dump
# 搜索：Found one Java-level deadlock
```

输出会指出 **持有什么锁、等待什么锁**、涉及线程名。

### 7.2 Arthas / JConsole

`thread -b` 找阻塞；JConsole 线程页检测死锁。

### 7.3 数据库

MySQL `SHOW ENGINE INNODB STATUS` 查看 LATEST DETECTED DEADLOCK。

---

## 8. 避免策略

| 策略 | 说明 |
|------|------|
| **固定加锁顺序** | 全局对资源 ID 排序后再加锁 |
| **tryLock 超时** | `lock.tryLock(1, SECONDS)` 失败则释放已持锁、重试或放弃 |
| **缩小锁粒度** | 减少持锁时间 |
| **无锁/CAS** | 能避免锁则避免 |
| **死锁检测** | 银行家算法（少用）；生产靠顺序+超时 |

```java
// 按 resourceId 排序后加锁
List<Long> ids = Arrays.asList(id1, id2);
Collections.sort(ids);
for (Long id : ids) {
    lock(id);
}
```

---

## 9. 活锁与饥饿

| 现象 | 说明 |
|------|------|
| **活锁** | 线程未阻塞但互相让步，无法前进（如两人走廊相遇一直让路） |
| **饥饿** | 低优先级或 unfair 锁长期得不到资源 |

ReentrantLock 公平锁可缓解饥饿，吞吐略降。

---

## 10. 面试题精选

**Q：ThreadLocal 为什么 key 用弱引用？**  
A：ThreadLocal 外部无强引用时可回收，避免 ThreadLocal 对象本身泄漏；但 value 仍需 `remove()`，因 Entry 仍强引用 value。

**Q：父子线程如何传递 ThreadLocal？**  
A：默认不传递；`InheritableThreadLocal` 在 **创建子线程时** copy；线程池下用 TTL 或手动传递。

**Q：如何破坏循环等待？**  
A：全局统一加锁顺序，或对资源编号排序。

---

## 11. 本章小结

- ThreadLocal + 线程池 = **必须 finally remove**。
- 死锁排查靠 **jstack**；预防靠 **加锁顺序 + tryLock 超时**。

← [05 线程池](./05-线程池ThreadPoolExecutor.md) · [07 CompletableFuture](./07-CompletableFuture与虚拟线程.md)
