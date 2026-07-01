# 04 · Set · Queue · Deque

> **目标读者**：7 年 Java 后端，需能选型 Set/Queue，理解 PriorityQueue 堆实现与 BlockingQueue 在生产者-消费者中的用法。
> **预计阅读**：50 min · **难度**：★★★

---

## 1. Set 体系

```
Set<E>
├── HashSet           ← 底层 HashMap，元素存 key
├── LinkedHashSet     ← 插入序
├── TreeSet           ← 红黑树有序
└── ConcurrentHashMap.newKeySet()  ← 并发 Set
```

### 1.1 HashSet 原理

```java
public class HashSet<E> {
    private transient HashMap<E, Object> map;
    private static final Object PRESENT = new Object();  // 占位 value

    public boolean add(E e) {
        return map.put(e, PRESENT) == null;
    }
}
```

| 实现 | 有序 | 复杂度 | 允许 null |
|------|------|--------|-----------|
| HashSet | 否 | O(1) | 1 个 |
| LinkedHashSet | 插入序 | O(1) | 1 个 |
| TreeSet | 排序 | O(log n) | 否 |

**去重依赖**：`hashCode` + `equals`，与 HashMap key 规则相同。

---

## 2. Queue 与 Deque

```
Queue
├── PriorityQueue      ← 堆，优先级
├── ArrayDeque         ← 数组双端队列（**栈/队列首选**）
├── LinkedList         ← 不推荐作队列
└── BlockingQueue
    ├── ArrayBlockingQueue
    ├── LinkedBlockingQueue
    ├── SynchronousQueue
    ├── DelayQueue
    └── PriorityBlockingQueue
```

| 接口方法 | 抛异常 | 返回特殊值 |
|----------|--------|------------|
| 入队 | add | offer |
| 出队 | remove | poll |
| 窥视 | element | peek |

---

## 3. PriorityQueue（小顶堆）

```java
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
```

| 项 | 说明 |
|----|------|
| 底层 | 数组实现的**二叉堆** |
| 插入/删除 | O(log n) |
| 窥顶 | O(1) |
| 线程安全 | **否** |
| 迭代顺序 | **非排序序**，仅保证 poll 顺序 |

```java
// TopK：维护大小为 K 的小顶堆
PriorityQueue<Integer> heap = new PriorityQueue<>(K);
for (int x : stream) {
    heap.offer(x);
    if (heap.size() > K) heap.poll();
}
```

**面试**：`PriorityQueue` 不是线程安全的；并发用 `PriorityBlockingQueue`。

---

## 4. ArrayDeque

- 循环数组实现双端队列。
- **不允许 null**（便于区分空与元素）。
- 扩容 2 倍；比 LinkedList 内存紧凑、缓存友好。

```java
Deque<Task> queue = new ArrayDeque<>();
queue.offerLast(task);   // 队尾入
Task t = queue.pollFirst();  // 队头出

// 作栈
deque.push(x);
deque.pop();
```

---

## 5. BlockingQueue 家族

### 5.1 对比

| 实现 | 底层 | 有界 | 特点 |
|------|------|------|------|
| ArrayBlockingQueue | 数组 + 一把锁 | **必须指定** | 公平/非公平可选 |
| LinkedBlockingQueue | 链表 + 两把锁 | 可选（默认 Integer.MAX_VALUE） | 吞吐高，注意无界 OOM |
| SynchronousQueue | 不存元素 | 0 容量 | 直接交接，线程池常用 |
| DelayQueue | PriorityQueue | 无界 | 延迟到期才可取 |

### 5.2 生产者-消费者

```java
BlockingQueue<Order> queue = new LinkedBlockingQueue<>(1000);

// 生产者
queue.put(order);           // 满则阻塞
queue.offer(order, 1, SECONDS);  // 超时

// 消费者
Order o = queue.take();     // 空则阻塞
```

**线程池**：`ThreadPoolExecutor` 用 `BlockingQueue` 作任务队列；`SynchronousQueue` + 最大线程 → 类似 CachedThreadPool。

---

## 6. DelayQueue 与 ScheduledThreadPool

```java
class DelayedTask implements Delayed {
    public long getDelay(TimeUnit u) {
        return deadline - System.currentTimeMillis();
    }
    public int compareTo(Delayed o) { ... }
}
DelayQueue<DelayedTask> dq = new DelayQueue<>();
```

`ScheduledThreadPoolExecutor` 内部用 `DelayedWorkQueue`（类似 DelayQueue）。

---

## 7. 并发 Set

```java
// JDK8+
Set<String> concurrentSet = ConcurrentHashMap.newKeySet();

// 或
Set<String> set = Collections.newSetFromMap(new ConcurrentHashMap<>());
```

CopyOnWriteArraySet 基于 COWAList，读多写少场景。

---

## 8. 选型速查

| 需求 | 选择 |
|------|------|
| 去重无序 | HashSet |
| 去重保插入序 | LinkedHashSet |
| 去重排序 | TreeSet |
| 并发去重 | CHM.newKeySet() |
| 任务调度 TopK | PriorityQueue |
| 线程池任务队列 | LinkedBlockingQueue / SynchronousQueue |
| 延迟任务 | DelayQueue |

---

## 9. 面试要点

| 问 | 答 |
|----|-----|
| HashSet 如何保证唯一？ | HashMap put key，PRESENT 占位 |
| PriorityQueue 底层？ | 数组二叉堆，非完全排序 |
| ArrayBlockingQueue vs Linked？ | 数组有界一把锁 vs 链表可选界两把锁 |
| SynchronousQueue 用途？ | 直接传递，Executors.newCachedThreadPool |
| 为什么队列推荐 Deque 不用 Stack？ | Stack 继承 Vector 遗留；Deque API 更清晰 |

---

## 10. 自测

- [ ] 手写 TopK with PriorityQueue
- [ ] 说明 LinkedBlockingQueue 无界风险
- [ ] 画 BlockingQueue put/take 阻塞语义

← [03-ConcurrentHashMap](./03-ConcurrentHashMap.md) · 下一章：[05-集合选型与fail-fast](./05-集合选型与fail-fast.md)
