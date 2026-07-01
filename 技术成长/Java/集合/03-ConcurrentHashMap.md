# 03 · ConcurrentHashMap

> **目标读者**：7 年 Java 后端，需能解释 CHM JDK7/8 锁粒度、size 计数，并在高并发场景正确选型。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 并发 Map 对比

| 实现 | 锁粒度 | null | 性能 | 现状 |
|------|--------|------|------|------|
| Hashtable | **整表** synchronized | 不允许 | 差 | 淘汰 |
| Collections.synchronizedMap | 每个方法锁 | 允许 | 一般 | 简单场景 |
| ConcurrentHashMap | **桶级** | 不允许 | 高 | **首选** |

**为什么 CHM 不允许 null？** `get(key)` 返回 null 无法区分「不存在」与「值为 null」，并发下歧义更大。

---

## 2. JDK 7：Segment 分段锁

```
ConcurrentHashMap
├── Segment[0]  (继承 ReentrantLock，独立 HashEntry[])
├── Segment[1]
└── Segment[n-1]   默认 concurrencyLevel=16 → 16 段
```

| 项 | 说明 |
|----|------|
| 结构 | Segment 数组 + 每段内 HashEntry 数组 + 链表 |
| 锁 | **Segment 级** ReentrantLock |
| size | 尝试 2 次不加锁统计；不一致则锁所有 Segment |
| 扩容 | **每 Segment 独立**扩容 |

**局限**：Segment 数量固定，极端热点段仍竞争；维护复杂。

---

## 3. JDK 8+：CAS + synchronized 桶头

```
Node[] table
  [i] → null          → put 时 CAS 放首节点
  [i] → Node 链表/树   → synchronized 锁**头节点**再操作
```

### 3.1 put 流程

```
1. 若 table 未初始化 → 协助 initTable（CAS）
2. 桶空 → CAS 放 Node
3. 桶非空 → synchronized(table[i]) {
       首节点 hash=-1 → 协助扩容 transfer
       否则链表插入/树插入/覆盖
   }
4. addCount(1) → 更新 size（CounterCell）
5. 超 threshold → transfer 扩容（多线程协助）
```

```java
// 简化：锁的是 table[i] 这个引用作为 monitor
synchronized (f) {  // f = table[i] 头节点
    // 链表或红黑树操作
}
```

**锁粒度**：一个桶一把锁，不同桶并行；比 Segment 更细。

### 3.2 initTable 与 transfer

- 初始化、扩容用 **CAS + 协作**：线程帮助迁移桶，`-1` 占位符表示 ForwardingNode。
- 扩容 **2 倍**，迁移逻辑类似 HashMap `(hash & oldCap)` 判断高低链。

---

## 4. size 计数：LongAdder 思想

```
baseCount（AtomicLong）
+ CounterCell[]（分散累加，减少 CAS 竞争）
→ sum() 求和得近似 size
```

| 方法 | 说明 |
|------|------|
| size() | 可能 **不精确**（求和瞬间无全局锁） |
| mappingCount() | JDK8+ 推荐，语义同 size |
| 精确场景 | 需全局锁或外部计数 |

---

## 5. get 操作

- **无锁**读：volatile 读 table 引用 + 链表/树遍历。
- 可见性：Node 的 val/next 用 volatile 或 synchronized 保证。
- 弱一致迭代器：反映创建后某一时刻状态，不抛 CME。

---

## 6. 常用 API 与陷阱

```java
// 原子 put-if-absent
map.putIfAbsent(key, value);

// JDK8 批量操作（并行）
map.forEach(1, (k, v) -> ...);   // parallelismThreshold
map.search(1, (k, v) -> ...);
map.reduce(1, (k, v) -> ..., (a, b) -> ...);

// 线程安全 Set
Set<K> keys = ConcurrentHashMap.newKeySet();
```

| 陷阱 | 说明 |
|------|------|
| `size()` 作严格判断 | 并发下不准，别 `if (map.size() == 0)` 做关键逻辑 |
| 复合操作 | `if (!contains) put` 非原子，用 `putIfAbsent` |
| compute 重入 | 同一 key 的 compute 回调里再改同一 key 可能死锁 |

```java
// ❌ 非原子
if (!map.containsKey(k)) map.put(k, v);
// ✅
map.putIfAbsent(k, v);
```

---

## 7. CHM vs HashMap 选型

| 场景 | 选择 |
|------|------|
| 单线程 / 局部变量 | HashMap |
| 多线程共享缓存 | ConcurrentHashMap |
| 需要 null value | HashMap + 外部同步，或 `Optional` 包装 |
| 读极多写极少 | COW 或 ImmutableMap + 定期替换 |
| 高并发 + 批量统计 | 外部 LongAdder / Redis |

---

## 8. 与 Hashtable 面试对比

| 问 | Hashtable | ConcurrentHashMap |
|----|-----------|-------------------|
| 锁 | 方法级整表 | 桶级 |
| 迭代器 | fail-fast | 弱一致 |
| null | 不允许 | 不允许 |
| 扩容 | 单线程 | 多线程协助 |

---

## 9. 面试要点

| 问 | 答 |
|----|-----|
| JDK7 和 JDK8 CHM 区别？ | Segment 分段锁 → CAS + synchronized 桶头 |
| 为什么废弃 Segment？ | 锁粒度可更细；实现与 HashMap 统一 |
| get 需要加锁吗？ | 不需要，volatile + 安全发布 |
| 1.7 能锁分段为什么 1.8 锁节点？ | 链表/树头作为 monitor，更细粒度 |
| 如何保证并发安全又不全表锁？ | CAS 空桶 + 桶头 synchronized |

---

## 10. 自测

- [ ] 白板画 JDK8 put 流程
- [ ] 解释 size 为什么不精确
- [ ] 对比 Segment 与 synchronized 桶头

← [02-HashMap与Map体系](./02-HashMap与Map体系.md) · 下一章：[04-Set-Queue与Deque](./04-Set-Queue与Deque.md)
