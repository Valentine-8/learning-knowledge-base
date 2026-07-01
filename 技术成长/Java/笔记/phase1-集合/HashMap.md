# HashMap 源码笔记

> Phase 1 · 集合框架  
> 状态：☐ 待学习 / 🔄 进行中 / ✅ 已完成  
> 关联项目：[mini-hashmap](../../../00-通用/项目实战清单.md#p01mini-hashmap)

---

## 核心结论（JDK 8）

| 项 | 说明 |
|----|------|
| 结构 | 数组 + 链表 + 红黑树 |
| 树化阈值 | 链表长度 ≥ 8 且数组长度 ≥ 64 |
| 退化阈值 | 树节点 ≤ 6 退化为链表 |
| 默认负载因子 | 0.75 |
| 扩容 | 2 倍，`rehash` |
| 线程安全 | **否**（JDK7 并发扩容可能死循环，JDK8 优化但仍非线程安全） |

---

## put 流程

1. `hash(key)` 扰动（高 16 位参与，减少碰撞）
2. 桶下标 `(n-1) & hash`
3. 桶空 → 直接放 Node
4. 否则：比 key（先 hash 再 equals）；相同则覆盖 value；不同则尾插链表/树
5. `++size`，若 `size > threshold`（capacity × loadFactor）→ **resize**

---

## 与 ConcurrentHashMap 对比

| | HashMap | ConcurrentHashMap |
|---|---------|-------------------|
| 线程安全 | 否 | 是 |
| JDK8 实现 | — | synchronized + CAS |
| null key/value | 允许 | **不允许** |

---

## 源码阅读清单

- [ ] `hash()` 扰动函数  
- [ ] `putVal`  
- [ ] `resize` 迁移  
- [ ] `getNode`  
- [ ] 红黑树 `treeifyBin`  

---

## 面试常问

1. HashMap 为什么线程不安全？  
2. JDK7 和 JDK8 区别？  
3. 为什么容量是 2 的幂？  
4. equals 和 hashCode 契约？  

---

## 自测

- [ ] 白板画 put 全流程  
- [ ] 手写 mini-hashmap（见项目 P01）  

---

*上一篇：[ArrayList.md](./ArrayList.md) · 下一篇：[ConcurrentHashMap.md](./ConcurrentHashMap.md)*
