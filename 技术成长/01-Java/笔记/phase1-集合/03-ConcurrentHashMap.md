# ConcurrentHashMap 源码笔记

> Phase 1 · 集合框架  
> 状态：☐ 待学习

---

## 核心结论

| 版本 | 实现 |
|------|------|
| JDK7 | Segment 分段锁 |
| JDK8+ | Node 数组 + synchronized 首节点 + CAS |

---

## 待补充

- [ ] `put` 流程  
- [ ] `size` 计数  
- [ ] 与 HashTable 区别  

---

*上一篇：[02-HashMap.md](./02-HashMap.md)*
