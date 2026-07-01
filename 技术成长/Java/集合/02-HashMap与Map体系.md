# 02 · HashMap 与 Map 体系

> **目标读者**：7 年 Java 后端，需能白板 HashMap put/resize，设计 LRU，并在面试中对比 LinkedHashMap / TreeMap。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. Map 体系全景

```
Map<K,V>
├── HashMap           ← 默认无序，O(1) 均摊
├── LinkedHashMap     ← 插入序 / accessOrder LRU
├── TreeMap           ← 红黑树，key 有序 O(log n)
├── Hashtable         ← 线程安全，已淘汰
├── ConcurrentHashMap ← 并发（见第 03 章）
└── WeakHashMap       ← 弱引用 key，GC 友好缓存
```

| 实现 | 有序性 | null key | 线程安全 | 时间复杂度 |
|------|--------|----------|----------|------------|
| HashMap | 无序 | 允许 1 个 | 否 | O(1) 均摊 |
| LinkedHashMap | 插入/访问序 | 同 HashMap | 否 | O(1) 均摊 |
| TreeMap | key 排序 | 不允许 | 否 | O(log n) |
| Hashtable | 无序 | **不允许** | synchronized | O(1) |

---

## 2. HashMap 结构（JDK 8）

```
table[]  ──►  [0] → null
              [1] → Node → Node → TreeNode（链表 ≥8 且 table≥64 树化）
              [2] → ...
              [15]→ ...
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 初始容量 | 16 | 必须是 2 的幂 |
| 负载因子 | 0.75 | 空间与碰撞折中 |
| 树化阈值 | 8 | 链表长度 ≥ 8 **且** 数组 ≥ 64 |
| 退树阈值 | 6 | resize 或删除后 ≤ 6 退链表 |
| 扩容 | 2 倍 | threshold = capacity × loadFactor |

**为什么容量 2 的幂？** 桶下标 `(n - 1) & hash` 等价 `hash % n` 且位运算更快；扩容时节点要么留原桶，要么去 `原下标 + oldCap`。

---

## 3. hash 扰动与定位

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

高 16 位参与异或，减少低位碰撞（数组较小时仍分布均匀）。

```java
// 桶下标
index = (table.length - 1) & hash;
```

---

## 4. put 全流程

```
1. hash(key)
2. 若 table 空 → resize 初始化
3. 桶空 → CAS 放首 Node（CHM）/ 直接放（HashMap）
4. 桶非空：
   a. 首节点 hash/key 相同 → 覆盖 value
   b. 红黑树 → tree.putTreeVal
   c. 链表 → 尾插比 key；达树化条件 → treeifyBin
5. ++size；若 size > threshold → resize
```

```java
// 简化伪代码
final V putVal(int hash, K key, V value, ...) {
    if (table == null || table.length == 0) resize();
    if (table[i = (n - 1) & hash] == null)
        table[i] = newNode(hash, key, value, null);
    else {
        // 比 hash、equals，链表或树插入/覆盖
    }
    if (++size > threshold) resize();
    return oldValue;
}
```

---

## 5. resize 迁移

- 新容量 = 旧容量 × 2，新 threshold 重新计算。
- 每个节点：`e.hash & oldCap == 0` → 留原索引；否则 → `原索引 + oldCap`。
- **JDK7 头插** 多线程 resize 可能死循环；**JDK8 尾插** 修复但仍非线程安全。

```java
// 初始容量预估，避免频繁 resize
int n = (int) (expectedSize / 0.75f + 1);
Map<K,V> map = new HashMap<>(n);
```

---

## 6. equals 与 hashCode 契约

```java
@Override
public boolean equals(Object o) { ... }

@Override
public int hashCode() {
    return Objects.hash(field1, field2);  // 与 equals 一致
}
```

| 规则 | 说明 |
|------|------|
| equals 相等 | hashCode **必须**相等 |
| hashCode 相等 | equals 不一定相等 |
| 自定义 key | **必须**同时重写 equals 和 hashCode |

**Integer 陷阱**：`-128~127` 缓存，`==` 与 `equals` 行为不同；作 key 用 `equals` 比较。

---

## 7. LinkedHashMap 与 LRU

```java
// accessOrder=true：get 会把节点移到链表尾部
Map<String, Integer> lru = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Integer> eldest) {
        return size() > MAX_SIZE;
    }
};
```

| 模式 | accessOrder | 顺序 |
|------|-------------|------|
| 插入序 | false（默认） | 先插入在前 |
| LRU | true | 最近访问在后， eldest 在头 |

底层在 HashMap.Node 上增加 `before/after` 双向链表维护顺序。

---

## 8. TreeMap

- 红黑树，按 key 自然序或 `Comparator`。
- `O(log n)` get/put；**不允许 null key**（compareTo NPE）。
- 场景：范围查询 `subMap`、`headMap`、`tailMap`。

```java
NavigableMap<Integer, String> map = new TreeMap<>();
map.subMap(10, true, 20, false);  // [10, 20)
```

---

## 9. JDK7 vs JDK8 差异

| 项 | JDK7 | JDK8+ |
|----|------|-------|
| 结构 | 数组 + 链表 | 数组 + 链表 + 红黑树 |
| 插入 | 头插 | 尾插 |
| hash | 4 次扰动 | 1 次扰动 |
| 并发 resize | 可能死循环 | 不会死循环但仍丢数据 |

---

## 10. 面试要点

| 问 | 答 |
|----|-----|
| HashMap 线程不安全表现？ | 覆盖/丢失；JDK7 resize 死循环 |
| 为什么负载因子 0.75？ | 统计学经验值，碰撞与空间平衡 |
| HashMap 和 Hashtable？ | HashMap 允许 null、更快；Hashtable 全表锁 |
| 手写 LRU？ | LinkedHashMap accessOrder + removeEldestEntry |
| 树化为什么要求数组 ≥64？ | 避免小 table 上链表短时到 8 就树化，浪费 |

---

## 11. 自测

- [ ] 白板画 put + resize
- [ ] 解释 `(n-1)&hash` 与扩容迁移
- [ ] 实现 LinkedHashMap LRU（见项目 P02）

← [01-List与ArrayList](./01-List与ArrayList.md) · 下一章：[03-ConcurrentHashMap](./03-ConcurrentHashMap.md)
