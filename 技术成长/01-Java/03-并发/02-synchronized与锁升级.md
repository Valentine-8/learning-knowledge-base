# 02 · synchronized 与锁升级

> **目标读者**：7 年 Java 后端，能讲清 synchronized 锁对象、锁升级路径、对象头 Mark Word，并对比 ReentrantLock 选型。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. synchronized 三种用法

| 用法 | 锁对象 | 作用范围 |
|------|--------|----------|
| 实例方法 | 当前实例 `this` | 同一实例互斥 |
| 静态方法 | 类的 `Class` 对象 | 全类互斥 |
| 代码块 | 括号内指定对象 | 自定义粒度 |

```java
public synchronized void instanceMethod() { }          // 锁 this

public static synchronized void staticMethod() { }   // 锁 Class

public void block() {
    synchronized (lockObject) {                      // 锁指定对象
        // critical section
    }
}
```

**可重入**：同一线程可多次获取同一把锁（计数 +1），避免自己锁死自己。

---

## 2. 对象头与 Mark Word

HotSpot 中每个 Java 对象都有对象头，其中 **Mark Word** 存储哈希码、GC 年龄、**锁状态** 等。

```
无锁 → 偏向锁 → 轻量级锁 → 重量级锁
```

| 锁状态 | 竞争情况 | 实现 |
|--------|----------|------|
| **偏向锁** | 几乎无竞争，同一线程反复进入 | 记录线程 ID，再次进入无需 CAS |
| **轻量级锁** | 少量竞争，持锁时间短 | 栈上 Lock Record + CAS |
| **重量级锁** | 激烈竞争或持锁时间长 | OS Mutex，线程 park/unpark |

**JDK 15+**：偏向锁默认关闭（`-XX:-UseBiasedLocking`）；JDK 18 起移除偏向锁。面试仍可能问历史演进，实际以 **轻量→重量** 为主。

---

## 3. 锁升级流程（简化）

```
线程访问 synchronized
    │
    ├─ 偏向锁成功（同线程）→ 直接执行
    │
    ├─ 其他线程竞争 → 撤销偏向 → 轻量级锁 CAS
    │       │
    │       ├─ CAS 成功 → 执行
    │       └─ CAS 失败 / 自旋过多 → 膨胀为重量级锁
    │
    └─ 重量级锁 → 进入 Monitor，未获锁线程 park
```

**自旋**：轻量锁阶段线程在用户态空转若干次，避免立即陷入内核；自旋失败再升级。

**锁降级**：HotSpot 几乎不做锁降级（与锁升级不对称），面试知道即可。

---

## 4. Monitor 与 synchronized 实现

synchronized 字节码：`monitorenter` / `monitorexit`。JVM 为每个对象关联一个 **Monitor**（C++ 实现）：

- `owner`：持锁线程
- `EntryList`：阻塞等待队列
- `WaitSet`：`wait()` 释放锁后进入

**释放时机**：正常退出同步块、异常退出（JVM 保证 monitorexit）、`wait()` 释放。

---

## 5. synchronized vs ReentrantLock

| 维度 | synchronized | ReentrantLock |
|------|--------------|---------------|
| 层次 | JVM 内置 | JUC API（基于 AQS） |
| 释放 | 自动 | 须 `unlock()`（finally 中） |
| 可中断 | 否 | `lockInterruptibly()` |
| 超时 | 否 | `tryLock(timeout)` |
| 公平锁 | 非公平 | 可选公平/非公平 |
| 多条件 | 单一 wait/notify | 多个 `Condition` |
| 性能 | JDK 6+ 优化后差距小 | 需手动管理 |

**选型建议**：

- 简单互斥、代码块短 → **synchronized**（简洁、不会忘记 unlock）
- 需要 tryLock、公平、多条件队列 → **ReentrantLock**
- 读多写少 → **ReadWriteLock**（见 [04 章](./04-AQS与JUC工具.md)）

---

## 6. 锁优化手段（JVM 层）

| 优化 | 说明 |
|------|------|
| 锁消除 | JIT 逃逸分析，栈上对象锁被消除 |
| 锁粗化 | 连续多次加锁合并为一次 |
| 自适应自旋 | 根据历史自旋成功率动态调整 |

这些对程序员透明，但说明 **无竞争时 synchronized 并不「很重」**。

---

## 7. 常见误用

```java
// 错误：锁 Integer 常量（-128~127 缓存池共享）
synchronized (count) { }  // count 是 Integer

// 错误：锁 this 但调用方传入不同实例 → 无互斥效果
public synchronized void update() { }

// 更好：锁明确的 private final Object lock = new Object();
```

**锁粒度**：锁整个方法 vs 只锁必要代码块；数据结构上能分段就分段（ConcurrentHashMap 思路）。

---

## 8. 与虚拟线程的交互（Java 21）

虚拟线程在 **synchronized 块内阻塞** 时可能 **pin（钉住）** 到载体 OS 线程，无法 unmount，削弱虚拟线程优势。优先用 `ReentrantLock` 或重构为无锁/异步 IO。

详见 [07 章](./07-CompletableFuture与虚拟线程.md)。

---

## 9. 面试题精选

**Q：synchronized 是可重入锁吗？**  
A：是。Mark Word / Monitor 记录重入次数，同线程再次进入计数 +1，退出 -1，为 0 时释放。

**Q：两个线程分别锁 obj1、obj2 会死锁吗？**  
A：若加锁顺序不一致可能死锁（见 [06 章](./06-ThreadLocal与死锁.md)）。

**Q：static synchronized 和实例 synchronized 能互斥吗？**  
A：不能。前者锁 Class，后者锁实例，锁对象不同。

---

## 10. 本章小结

- synchronized 锁的是 **对象**，不是代码或方法名。
- JDK 6+ 锁升级减少无竞争开销；高竞争仍走重量级 OS 锁。
- 与 ReentrantLock 按 **功能需求** 选型，非单纯比性能。

← [01 并发基础](./01-并发基础与happens-before.md) · [03 volatile](./03-volatile与CAS.md)
