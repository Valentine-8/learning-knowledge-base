# 04 · AQS 与 JUC 工具

> **目标读者**：7 年 Java 后端，能讲清 AQS 的 state + CLH 队列模型，并正确选用 ReentrantLock、Semaphore、CountDownLatch 等工具。
> **预计阅读**：60 min · **难度**：★★★★★

---

## 1. AQS 是什么

**AbstractQueuedSynchronizer** 是 JUC 同步器框架，`ReentrantLock`、`Semaphore`、`CountDownLatch`、`CyclicBarrier`、`ReentrantReadWriteLock`、线程池 Worker 均基于 AQS 或其变体。

核心结构：

```
┌─────────────────────────────────────┐
│  state（volatile int）               │  同步状态
├─────────────────────────────────────┤
│  CLH 双向队列（Node）                 │  等待线程 FIFO
│  head ← → node ← → node ← → tail   │
└─────────────────────────────────────┘
```

---

## 2. 获取与释放流程

**独占模式（ReentrantLock）**：

```
tryAcquire():
  1. state==0 → CAS 设为 1，成功则获锁
  2. 已是 owner 线程 → 重入，state++
  3. 失败 → 封装 Node 入队 tail，LockSupport.park 阻塞

release():
  1. state--，为 0 时释放
  2. 唤醒后继 head.next
```

**共享模式（Semaphore、ReadLock）**：`tryAcquireShared` 返回剩余许可数，<0 则排队。

---

## 3. Node 与等待队列

| 字段 | 含义 |
|------|------|
| waitStatus | CANCELLED、SIGNAL、CONDITION 等 |
| prev / next | 双向链表 |
| thread | 等待线程 |
| nextWaiter | 共享/条件队列链接 |

**为何 CLH 变体**：减少全局锁竞争，仅 tail 插入 CAS，唤醒后继。

**公平 vs 非公平**：

- 非公平：`tryAcquire` 先 CAS 抢，失败再排队（吞吐高，默认）
- 公平：检查队列是否有前驱，有则排队（防饥饿）

---

## 4. ReentrantLock

```java
ReentrantLock lock = new ReentrantLock(true);  // 公平锁

lock.lock();
try {
    // critical section
} finally {
    lock.unlock();  // 必须在 finally
}

// 可中断
lock.lockInterruptibly();

// 超时
if (lock.tryLock(3, TimeUnit.SECONDS)) {
    try { ... } finally { lock.unlock(); }
}
```

**Condition**（替代 wait/notify）：

```java
Condition notEmpty = lock.newCondition();
Condition notFull = lock.newCondition();

// 生产者
lock.lock();
try {
    while (queue.isFull()) notFull.await();
    queue.add(item);
    notEmpty.signal();
} finally { lock.unlock(); }
```

一个 Lock 可创建 **多个 Condition**，精确唤醒（如阻塞队列的生产/消费）。

---

## 5. ReadWriteLock

```java
ReadWriteLock rw = new ReentrantReadWriteLock();
Lock readLock = rw.readLock();
Lock writeLock = rw.writeLock();
```

| 锁 | 互斥关系 |
|----|----------|
| 读-读 | 不互斥 |
| 读-写 | 互斥 |
| 写-写 | 互斥 |

**场景**：配置缓存、字典读多写少。写锁降级：持写锁 → 获取读锁 → 释放写锁（AQS 支持）。

**StampedLock**（JDK 8）：乐观读 `tryOptimisticRead()`，适合读极多、写极少，不可重入，API 复杂。

---

## 6. Semaphore（信号量）

```java
Semaphore sem = new Semaphore(10);  // 10 个许可

sem.acquire();   // 许可 -1，无许可则阻塞
try {
    // 访问连接池 / 限流
} finally {
    sem.release();
}
```

**state 含义**：剩余许可数。用于 **限流**、连接池并发上限、停车场模型。

`tryAcquire(n)`、`release(n)` 支持一次申请/释放多个许可。

---

## 7. CountDownLatch（倒计时门闩）

```java
CountDownLatch latch = new CountDownLatch(3);

// 工作线程
latch.countDown();

// 主线程等待
latch.await();  // 直到计数为 0
```

- **一次性**：计数不能重置
- **场景**：等多线程任务完成再汇总；服务启动等待依赖就绪

---

## 8. CyclicBarrier（循环栅栏）

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("all arrived"));

barrier.await();  // 第 3 个到达时触发 barrierAction，然后全部继续
```

- **可循环** reuse
- **场景**：分阶段并行计算，每阶段齐再进入下一阶段

**对比 Latch**：Latch 是一个等多个；Barrier 是多个互相等。

---

## 9. Phaser（分阶段屏障）

更灵活的 `CyclicBarrier`：动态注册/注销参与者、分阶段（phase）编号。MapReduce 式多阶段任务可用，日常业务 **CountDownLatch / CyclicBarrier 足够**。

---

## 10. 其他 JUC 工具速览

| 类 | 场景 |
|----|------|
| `Exchanger` | 两线程交换数据 |
| `DelayQueue` | 延迟任务 |
| `TransferQueue` | 生产者阻塞直到消费者 take |

---

## 11. 面试题精选

**Q：AQS 的 state 在不同组件里含义？**  
A：ReentrantLock=重入次数；Semaphore=许可数；CountDownLatch=剩余计数；ReadWriteLock 高 16 位写锁、低 16 位读锁。

**Q：为什么 unpark 可以唤醒指定线程，而 notify 随机？**  
A：`LockSupport.unpark(thread)` 精确唤醒；`Object.notify()` 由 JVM 从 WaitSet 选一个。

**Q：线程池 Worker 如何用 AQS？**  
A：Worker 继承 AQS，实现不可重入互斥锁，保证一个 Worker 同一时刻只执行一个任务，并支持中断空闲 Worker。

---

## 12. 本章小结

- 理解 AQS = **state + 队列 + park/unpark**，即可读懂大部分 JUC 锁。
- 按场景选工具：互斥用 Lock，限流用 Semaphore，等多线程完成用 Latch，分阶段齐步走用 Barrier。

← [03 volatile](./03-volatile与CAS.md) · [05 线程池](./05-线程池ThreadPoolExecutor.md)
