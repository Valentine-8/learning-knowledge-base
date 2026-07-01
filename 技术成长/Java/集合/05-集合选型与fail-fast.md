# 05 · 集合选型与 fail-fast

> **目标读者**：7 年 Java 后端，需能在业务中正确选型集合、理解 fail-fast/fail-safe，掌握泛型 PECS 与 Stream 集合操作陷阱。
> **预计阅读**：50 min · **难度**：★★★

---

## 1. 场景选型决策树

```
需要键值对？
  ├─ 是 → 要线程安全？
  │        ├─ 是 → ConcurrentHashMap
  │        └─ 否 → 要顺序？
  │                 ├─ 插入/LRU → LinkedHashMap
  │                 ├─ 排序 → TreeMap
  │                 └─ 否 → HashMap
  └─ 否 → 要唯一？
           ├─ 是 → HashSet / TreeSet / LinkedHashSet
           └─ 否 → 要队列？
                    ├─ 是 → ArrayDeque / BlockingQueue
                    └─ 否 → ArrayList（默认 List）
```

---

## 2. 复杂度与场景对照

| 操作 | ArrayList | LinkedList | HashMap | TreeMap | CHM |
|------|-----------|------------|---------|---------|-----|
| get(i) | O(1) | O(n) | — | — | — |
| get(key) | — | — | O(1) | O(log n) | O(1) |
| 尾 add | O(1) 均摊 | O(1) | — | — | — |
| 中间 insert | O(n) | O(1)* | — | — | — |
| 遍历 | O(n) | O(n) | O(n+buckets) | O(n) | O(n) |

\* LinkedList 需先定位节点 O(n)。

---

## 3. fail-fast 机制

### 3.1 原理

```java
// ArrayList.Itr
final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

**结构性修改**：add/remove/set 改变 size 或内部结构（set 同一 index 替换不算）。

### 3.2 fail-fast 集合

| 集合 | 检测方式 |
|------|----------|
| ArrayList / Vector | modCount |
| HashMap | modCount（迭代 entrySet/keySet） |
| HashSet | 同 HashMap |

### 3.3 fail-safe / 弱一致

| 集合 | 机制 |
|------|------|
| CopyOnWriteArrayList | 迭代器持有数组**快照** |
| ConcurrentHashMap | 弱一致，不保证强一致快照 |
| ConcurrentLinkedQueue | 无锁 CAS，弱一致 |

```java
// COW：写时复制整个数组，读无锁
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
// 写慢读快，适合监听器列表、配置快照
```

---

## 4. 遍历与修改最佳实践

```java
// ❌ fail-fast
for (String s : list) {
    if (cond(s)) list.remove(s);
}

// ✅ Iterator.remove
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if (cond(it.next())) it.remove();
}

// ✅ JDK8+
list.removeIf(this::cond);

// Map
map.entrySet().removeIf(e -> cond(e.getValue()));
```

---

## 5. 不可变与包装集合

```java
List<String> immutable = List.of("a", "b");           // JDK9+，不可变
List<String> unmodifiable = Collections.unmodifiableList(mutable);  // 视图，底层仍可变

Collections.synchronizedList(list);   // 每个方法 synchronized
Collections.synchronizedMap(map);
```

| API | 特点 |
|-----|------|
| `List.of()` | 真正不可变，不允许 null |
| `unmodifiableXxx` | 视图，原集合改则变 |
| `synchronizedXxx` | 复合操作仍需外部同步 |

---

## 6. 泛型与 PECS

```java
// Producer Extends：只能读（作为 T 的来源）
void copy(List<? extends Number> src, List<? super Number> dest) {
    for (Number n : src) {
        dest.add(n);  // super 侧可写 Number 及子类
    }
}
```

| 通配符 | 读 | 写 |
|--------|----|----|
| `<? extends T>` | 当 T 读 | 不能 add（除 null） |
| `<? super T>` | 当 Object 读 | 可 add T 及子类 |

**类型擦除**：编译期检查，运行期 `List<String>` 擦成 `List`，反射可见泛型签名。

---

## 7. Stream 与集合

```java
Map<String, Long> count = list.stream()
    .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

Map<String, User> map = users.stream()
    .collect(Collectors.toMap(User::getId, u -> u,
        (a, b) -> a));  // 必须处理 key 冲突
```

| 陷阱 | 说明 |
|------|------|
| 并行流 | 共用 `ForkJoinPool.commonPool()`；小数据/IO 别用 |
| 外部可变 | `list.stream().forEach(x -> sum++);` ❌ |
| toMap 无 merge | 重复 key 抛 IllegalStateException |
| 有序 | parallel 可能打乱，需 `forEachOrdered` |

---

## 8. 初始容量与性能

```java
// HashMap：expectedSize / 0.75 + 1
new HashMap<>( (int)(size / 0.75f) + 1 );

// ArrayList
new ArrayList<>(size);

// StringBuilder 同理
```

| 问题 | 后果 |
|------|------|
| 默认容量 + 大量 add | 多次扩容 + arraycopy |
| HashMap 频繁 resize | rehash 全表迁移 |
| LinkedBlockingQueue 无界 | 生产者快于消费者 → OOM |

---

## 9. Java 8～21 集合相关新 API

| 版本 | API | 用途 |
|------|-----|------|
| 9 | `List.of`, `Map.of`, `Set.of` | 不可变小集合 |
| 10 | `copyOf` | 防御性拷贝为不可变 |
| 21 | SequencedCollection | 首尾元素统一 API |

```java
Map<String, Integer> m = Map.of("a", 1, "b", 2);  // 最多 10 对，无 null
SequencedCollection<String> seq = new ArrayList<>();
seq.getFirst(); seq.getLast();
```

---

## 10. 面试要点

| 问 | 答 |
|----|-----|
| fail-fast 和 fail-safe？ | modCount 抛异常 vs 快照/弱一致 |
| 遍历时删除？ | iterator.remove / removeIf |
| PECS 举例？ | Collections.copy extends/super |
| 如何设计线程安全 List？ | synchronizedList / COW / 外部锁 |
| unmodifiable 和 immutable？ | 视图 vs 真正不可变 |

---

## 11. 自测

- [ ] 给订单系统选 Map 和 Queue 并说明理由
- [ ] 解释 COW 写时复制成本
- [ ] 写一段 PECS 的 copy 方法

← [04-Set-Queue与Deque](./04-Set-Queue与Deque.md) · 下一章：[06-生产案例与面试题库](./06-生产案例与面试题库.md)
