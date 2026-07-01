# 03 · volatile 与 CAS

> **目标读者**：7 年 Java 后端，能讲清 volatile 语义、内存屏障、CAS 原理与 ABA 问题，并正确使用原子类。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. volatile 的两大作用

| 作用 | 机制 |
|------|------|
| **可见性** | 写立即刷新到主内存；读从主内存读，跳过工作内存 stale 值 |
| **禁止重排** | 插入内存屏障，保证 volatile 写之前的操作不会排到写之后 |

**不保证原子性**：`volatile int i; i++` 仍是读-改-写三步，多线程会丢更新。

---

## 2. 内存屏障（了解即可）

| 屏障 | 效果 |
|------|------|
| LoadLoad | 读-读：禁止后面的读重排到前面 |
| StoreStore | 写-写：volatile 写前的写不能排到写后 |
| LoadStore | 读-写 |
| StoreLoad | 写-读：最重，volatile 写后读须在此屏障后 |

HotSpot 在 volatile 读写处插入适当屏障，实现 JMM 的 happens-before。

---

## 3. 经典场景：DCL 单例

```java
public class Singleton {
    private volatile static Singleton inst;

    public static Singleton getInstance() {
        if (inst == null) {                          // 第一次检查，无锁
            synchronized (Singleton.class) {
                if (inst == null) {                  // 第二次检查
                    inst = new Singleton();
                }
            }
        }
        return inst;
    }
}
```

**为何需要 volatile**：`new Singleton()` 可能重排为：

1. 分配内存
2. 引用赋值（inst 非 null）
3. 调用构造器

其他线程可能在步骤 2 后看到 **半初始化对象**。volatile 禁止 2 排在 3 前。

---

## 4. volatile 适用场景

| 适合 | 不适合 |
|------|--------|
| 状态标志 `volatile boolean shutdown` | 计数器 `i++` |
| 双重检查锁的单例引用 | 复合操作（check-then-act） |
| 一写多读的配置字段 | 需要原子更新的共享变量 |

复合操作用 **synchronized、Lock 或 Atomic***。

---

## 5. CAS（Compare-And-Swap）

**语义**：`if (内存值 == 期望值) { 内存值 = 新值; return true; } else return false;`

CPU 提供原子指令（如 x86 `CMPXCHG`），JDK 通过 `Unsafe` 或 VarHandle 暴露。

```java
AtomicInteger counter = new AtomicInteger(0);
counter.compareAndSet(0, 1);  // 期望 0，设为 1
counter.incrementAndGet();      // 内部 CAS 循环
```

**优点**：无锁，高并发下减少阻塞。  
**缺点**：ABA 问题、自旋开销、只能保证单变量原子。

---

## 6. ABA 问题

线程 A 读值 A → 被挂起 → 线程 B 把 A 改成 B 再改回 A → A 的 CAS 仍成功，但中间状态已被破坏。

**解决**：`AtomicStampedReference` — 值 + **版本号（stamp）**，CAS 同时比较 stamp。

```java
AtomicStampedReference<String> ref =
    new AtomicStampedReference<>("A", 0);
ref.compareAndSet("A", "B", 0, 1);  // 期望 A 且 stamp=0
```

---

## 7. 常用原子类

| 类 | 用途 |
|----|------|
| `AtomicInteger/Long` | 计数、状态 |
| `AtomicReference` | 引用 CAS |
| `AtomicIntegerArray` | 数组元素原子更新 |
| `LongAdder` | **高并发累加**，分段 Cell，最终 sum |
| `DoubleAdder` | 浮点累加 |

### LongAdder vs AtomicLong

```
高并发写：
AtomicLong     → 单变量 CAS，竞争激烈时自旋多
LongAdder      → 分散到多个 Cell，最后 sum() 合并
```

**选型**：读多写少或低竞争用 `AtomicLong`；**高并发计数**（QPS 统计）用 `LongAdder`。

---

## 8. Unsafe 与 VarHandle（JDK 9+）

`sun.misc.Unsafe` 是 CAS 底层，不推荐业务直接使用。JDK 9 引入 **VarHandle** 作为标准替代，支持字段级 CAS 与内存排序。

框架与 JUC 源码大量依赖 CAS；业务层优先用 `java.util.concurrent.atomic` 包。

---

## 9. 伪共享（Cache Line）

`LongAdder` 的 Cell 使用 `@Contended`（或 padding）避免多个计数器落在同一 Cache Line，减少 CPU 缓存行 bouncing。

Disruptor 等高性能框架也做 Cache Line 填充。7 年工程师 **了解概念** 即可。

---

## 10. 面试题精选

**Q：volatile 和 synchronized 都能保证可见性，区别？**  
A：volatile 不互斥、不保证复合操作原子；synchronized 互斥且释放锁时刷主存。volatile 更轻但能力更小。

**Q：CAS 一定比锁快吗？**  
A：低竞争时常更快；高竞争时大量自旋可能不如阻塞锁，且占用 CPU。

**Q：AtomicInteger 的 getAndIncrement 如何实现？**  
A：循环 CAS：`do { old = get(); } while (!compareAndSet(old, old+1));`

---

## 11. 本章小结

- volatile = **可见 + 有序**，不是万能锁。
- CAS = 乐观锁基础，注意 **ABA** 与 **自旋成本**。
- 高并发计数首选 **LongAdder**。

← [02 synchronized](./02-synchronized与锁升级.md) · [04 AQS](./04-AQS与JUC工具.md)
