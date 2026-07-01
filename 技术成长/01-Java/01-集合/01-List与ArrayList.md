# 01 · List 与 ArrayList

> **目标读者**：7 年 Java 后端，需能解释 ArrayList 扩容、fail-fast，并在面试中对比 LinkedList / Vector / ArrayDeque。
> **预计阅读**：50 min · **难度**：★★★

---

## 1. List 接口体系

```
List<E>
├── ArrayList          ← 默认首选
├── LinkedList         ← 双向链表，队列场景被 ArrayDeque 替代
├── Vector             ← 线程安全，已淘汰
├── Stack              ← 继承 Vector，已不推荐
└── CopyOnWriteArrayList ← 并发读多写少
```

| 实现 | 底层 | 线程安全 | 随机访问 | 中间插入 |
|------|------|----------|----------|----------|
| ArrayList | 动态数组 | 否 | O(1) | O(n) |
| LinkedList | 双向链表 | 否 | O(n) | O(1) 已知节点 |
| Vector | 动态数组 + synchronized | 是 | O(1) | O(n) |
| CopyOnWriteArrayList | 写时复制数组 | 是 | O(1) | O(n) 写时复制全数组 |

---

## 2. ArrayList 核心机制

### 2.1 底层结构

```java
public class ArrayList<E> {
    transient Object[] elementData;  // 实际存储
    private int size;                // 元素个数，非 capacity
    private static final int DEFAULT_CAPACITY = 10;
}
```

| 项 | 说明 |
|----|------|
| 默认容量 | **10**（`new ArrayList()` 时 **不分配**，首次 `add` 才 `grow`） |
| 扩容倍数 | **1.5 倍**：`newCap = old + (old >> 1)` |
| 最大容量 | `Integer.MAX_VALUE - 8`（防 VM 限制） |
| 序列化 | `elementData` 可能有多余空位，自定义 `writeObject` 只写 size 个 |

### 2.2 扩容流程

```
add(e)
  → ensureCapacityInternal(size + 1)
  → ensureExplicitCapacity
  → grow(minCapacity)
  → newCapacity = old + (old >> 1)  // 1.5 倍
  → Arrays.copyOf 复制
```

```java
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

**为什么 1.5 倍？** 平衡空间浪费与复制次数；2 倍浪费多，1.2 倍 resize 更频繁。

### 2.3 指定位置插入

```java
public void add(int index, E element) {
    rangeCheckForAdd(index);
    ensureCapacityInternal(size + 1);
    System.arraycopy(elementData, index, elementData, index + 1, size - index);
    elementData[index] = element;
    size++;
}
```

中间 insert/remove 需 `arraycopy`，**O(n)**。随机读多用 ArrayList，中间频繁插删才考虑 LinkedList。

---

## 3. fail-fast 原理

ArrayList 迭代器维护 `expectedModCount`，与 `modCount` 不一致时抛 `ConcurrentModificationException`。

```java
for (String s : list) {
    if ("x".equals(s)) list.remove(s);  // ❌ 结构修改
}
// 正确：iterator.remove() 或 removeIf
list.removeIf("x"::equals);
```

| 操作 | modCount 变化 | 迭代器行为 |
|------|---------------|------------|
| add/remove（非迭代器） | +1 | fail-fast 抛异常 |
| iterator.remove() | 同步更新 expectedModCount | 安全 |

---

## 4. LinkedList 与 ArrayDeque

### 4.1 LinkedList

- 双向链表 + 实现 `Deque`。
- 每个节点额外 `prev/next` 指针，**内存开销大、缓存不友好**。
- JDK 官方文档：实现 Deque 时 **ArrayDeque 更高效**。

### 4.2 ArrayDeque

| 场景 | 推荐 |
|------|------|
| 栈 `push/pop` | ArrayDeque |
| 队列 `offer/poll` | ArrayDeque |
| 双端队列 | ArrayDeque |
| 需要 `List` 随机访问 | ArrayList |

```java
Deque<String> stack = new ArrayDeque<>();
stack.push("a");
stack.pop();
```

---

## 5. Vector 与 Stack（了解）

| 对比 | ArrayList | Vector |
|------|-----------|--------|
| 线程安全 | 否 | synchronized 方法 |
| 扩容 | 1.5 倍 | **2 倍** |
| 性能 | 高 | 低（方法级锁） |
| 现状 | 首选 | **已淘汰** |

`Stack` 继承 Vector，API 遗留；用 `ArrayDeque` 代替。

---

## 6. 常见陷阱

| 陷阱 | 说明 |
|------|------|
| `Arrays.asList(arr)` | 固定大小，不能 add/remove；底层是数组视图 |
| `subList(from, to)` | 原列表结构修改会导致 `ConcurrentModificationException` |
| `toArray()` | 返回 `Object[]`，需 `toArray(new String[0])` |
| 初始容量 | 已知大小用 `new ArrayList<>(n)` 避免多次扩容 |

```java
List<String> fixed = Arrays.asList("a", "b");
// fixed.add("c");  // UnsupportedOperationException

List<String> sub = list.subList(1, 3);
list.add("x");     // 之后 sub 操作可能异常
```

---

## 7. 面试要点

| 问 | 答 |
|----|-----|
| ArrayList 和 LinkedList？ | 数组 vs 链表；随机读 ArrayList O(1)；中间插删 LinkedList 理论 O(1) 但常数大 |
| 扩容为什么是 1.5 倍？ | 空间与复制次数折中 |
| fail-fast 原理？ | modCount + expectedModCount |
| 如何实现线程安全 List？ | `Collections.synchronizedList`、COWAList、或外部锁 |
| ArrayList 序列化？ | 只序列化有效元素，非整个 capacity |

---

## 8. 自测

- [ ] 白板画 `grow` 逻辑
- [ ] 解释 `subList` 与原列表关系
- [ ] 对比 ArrayDeque 与 LinkedList 内存布局

← [00-速查总览](./00-速查总览.md) · 下一章：[02-HashMap与Map体系](./02-HashMap与Map体系.md)
