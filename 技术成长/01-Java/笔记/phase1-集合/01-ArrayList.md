# ArrayList 源码笔记

> Phase 1 · 集合框架  
> 参考：[JavaGuide ArrayList 源码](https://javaguide.cn/java/collection/arraylist-source-code.html)  
> 关联项目：[项目实战清单 P02 LRU](../../../00-通用/12-项目实战清单.md)

---

## 核心结论

| 项 | 说明 |
|----|------|
| 底层结构 | 动态数组 `Object[] elementData` |
| 线程安全 | **否** |
| 默认容量 | 10（首次 add 时分配） |
| 扩容倍数 | **1.5 倍**（`oldCapacity + (oldCapacity >> 1)`） |
| 随机访问 | O(1) |
| 头插/中间插入 | O(n)，需 `System.arraycopy` |
| fail-fast | 迭代时 structurally modify 抛 `ConcurrentModificationException` |

---

## 与 LinkedList 选型

| 场景 | 选择 |
|------|------|
| 随机读多、尾插多 | ArrayList |
| 头插删多 | LinkedList 或 ArrayDeque |
| 队列/栈 | ArrayDeque 优先于 LinkedList |

---

## 扩容流程

1. `add` → `ensureCapacityInternal(size + 1)`  
2. `ensureExplicitCapacity` → 容量不足则 `grow`  
3. `grow`：新容量 = 旧容量 × 1.5，与 `minCapacity` 取大  
4. `Arrays.copyOf` 复制数组  

---

## 源码片段：add(index, element)

```java
public void add(int index, E element) {
    rangeCheckForAdd(index);
    ensureCapacityInternal(size + 1);
    System.arraycopy(elementData, index, elementData, index + 1, size - index);
    elementData[index] = element;
    size++;
}
```

---

## 源码片段：grow 扩容

```java
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);  // 1.5 倍
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

---

## 面试常问

1. **ArrayList 和 Vector 区别？**  
   Vector 线程安全（synchronized），扩容 2 倍，已过时。

2. **为什么扩容 1.5 倍？**  
   平衡空间浪费与复制次数。

3. **subList 要注意什么？**  
   原 list 结构修改会导致 subList 操作异常。

---

## 自测

- [ ] 能白板写出 grow 逻辑  
- [ ] 能解释 fail-fast 原理（modCount）  
- [ ] 能对比 ArrayDeque  

---

*下一篇：[02-HashMap.md](./02-HashMap.md)*
