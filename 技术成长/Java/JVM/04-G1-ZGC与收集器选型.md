# 04 · G1 · ZGC 与收集器选型

> **目标读者**：7 年 Java 后端，需能对比 Serial/Parallel/CMS/G1/ZGC，说明 G1 Region 与 Mixed GC，并在生产中选型与调参。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 收集器全景

```
新生代收集器          老年代收集器           全堆
Serial               Serial Old            —
Parallel Scavenge    Parallel Old          —
ParNew               CMS                   —
—                    —                     G1
—                    —                     ZGC / Shenandoah
```

| 收集器 | 区域 | 线程 | 停顿 | 现状 |
|--------|------|------|------|------|
| Serial | 新生代 | 单 | STW | 客户端 |
| Parallel Scavenge | 新生代 | 多 | STW | **吞吐优先** |
| ParNew | 新生代 | 多 | STW | 配 CMS |
| Serial Old | 老年代 | 单 | STW | 配 Serial |
| Parallel Old | 老年代 | 多 | STW | 配 PS |
| CMS | 老年代 | 并发 | 低停顿 | **逐步淘汰** |
| **G1** | Region 全堆 | 并发+STW | 可预测 | **JDK9+ 默认** |
| **ZGC** | 全堆 | 并发 | **<10ms 级** | JDK15+ 生产可用 |
| Shenandoah | 全堆 | 并发 | 低延迟 | OpenJDK |

---

## 2. CMS 简要（历史与面试）

```
Initial Mark (STW) → Concurrent Mark → Remark (STW) → Concurrent Sweep
```

| 优点 | 缺点 |
|------|------|
| 并发标记清除，低停顿 | **浮动垃圾**（并发阶段产生） |
| | **内存碎片** → Promotion Failed |
| | Concurrent Mode Failure → Full GC |
| | CPU 敏感 |

**已不推荐**新系统使用；面试常问 **G1 vs CMS**。

---

## 3. G1（Garbage First）

### 3.1 设计思想

- 堆划为等长 **Region**（1~32MB，2 的幂）。
- 每个 Region 可为 Eden / Survivor / Old / Humongous。
- 优先回收 **垃圾最多** 的 Region（Garbage First）。

```
┌────┬────┬────┬────┬────┬────┐
│ E  │ E  │ S  │ O  │ O  │ H  │  ... 数百 Region
└────┴────┴────┴────┴────┴────┘
  H = Humongous（大对象占连续 Region）
```

### 3.2 GC 类型

| 类型 | 说明 |
|------|------|
| Young GC | 回收所有 Eden + Survivor |
| Mixed GC | 回收新生代 + **部分**老年代 Region（并发标记后） |
| Full GC | 单线程 Serial Old 式，**要尽量避免** |

### 3.3 并发标记周期

```
Initial Mark (STW) → Root Region Scan → Concurrent Mark
→ Remark (STW) → Cleanup → Mixed GC 若干次
```

### 3.4 关键参数

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200        # 目标停顿（非保证）
-XX:G1HeapRegionSize=16m
-XX:InitiatingHeapOccupancyPercent=45   # 堆占用 45% 启动并发标记
-XX:G1MixedGCCountTarget=8
```

**选型**：通用 Web、微服务、**堆 4G~几十 G** → G1 默认首选。

---

## 4. ZGC（Z Garbage Collector）

### 4.1 特点

- **并发**标记、并发整理、并发引用处理。
- 目标停顿 **亚毫秒~10ms 级**，与堆大小 **弱相关**（TB 级堆仍低延迟）。
- JDK15+ **Production Ready**；JDK21 分代 ZGC 可选。

### 4.2 染色指针（Colored Pointers）

64 位指针中借位存 GC 状态，Load Barrier 根据颜色决定是否修正引用。

```
┌──────────────────────────────────────┐
│ 指针位：Marked0 / Marked1 / Remapped  │
└──────────────────────────────────────┘
```

### 4.3 参数

```bash
-XX:+UseZGC
-XX:+ZGenerational        # JDK21+ 分代 ZGC
-Xmx16g                   # 大堆场景
```

| 适用 | 不适用 |
|------|--------|
| 超大堆（100G+） | 小堆（<4G 收益不明显） |
| P99 延迟极敏感（交易、游戏） | 纯批处理要吞吐 |
| 愿意用较新 JDK | 老 JDK8 无法用 |

---

## 5. Parallel GC（吞吐型）

```bash
-XX:+UseParallelGC    # 默认 PS + Parallel Old
-XX:GCTimeRatio=99    # 吞吐目标
-XX:MaxGCPauseMillis=...  # 与 G1 不同，作软目标
```

- **最大化吞吐量**，停顿可较长。
- 适合离线计算、批处理、大数据 ETL。

---

## 6. 选型决策

```
延迟敏感 + 大堆？
  ├─ 是 → ZGC（JDK17+）或 Shenandoah
  └─ 否 → 吞吐批处理？
           ├─ 是 → Parallel GC
           └─ 否 → G1（默认）
```

| 场景 | 推荐 | 堆参考 |
|------|------|--------|
| Spring Boot 微服务 | G1 | 2~8G |
| 电商核心交易 | G1 或 ZGC | 8~32G |
| 报表 / Spark Driver | Parallel | 大 |
| 遗留 JDK8 | G1 或 CMS | — |

---

## 7. G1 vs CMS vs ZGC 对比表

| 维度 | CMS | G1 | ZGC |
|------|-----|-----|-----|
| 碎片 | 有 | 整理，无 | 整理 |
| 浮动垃圾 | 有 | 有但可控 | 并发处理 |
| 停顿目标 | 尽力 | MaxGCPauseMillis | 极低 |
| Full GC 风险 | CMC Failure | 应避免 | 极少 |
| JDK | 8（废弃趋势） | 9+ 默认 | 15+ |

---

## 8. 面试要点

| 问 | 答 |
|----|-----|
| G1 和 CMS？ | G1 Region、Mixed GC、无碎片；CMS 并发清除有碎片 |
| G1 如何控停顿？ | 回收集选 Region、可设 MaxGCPauseMillis |
| ZGC 低延迟原理？ | 染色指针 + Load Barrier + 并发整理 |
| 什么时候 Full GC？ | G1 分配失败、并发标记来不及等 |
| JDK9 默认收集器？ | G1 |

---

## 9. 自测

- [ ] 画 G1 Region 示意图
- [ ] 给 16G 堆交易服务选 GC 并写参数
- [ ] 解释 CMS Concurrent Mode Failure

← [03-垃圾回收算法与分代](./03-垃圾回收算法与分代.md) · 下一章：[05-类加载与双亲委派](./05-类加载与双亲委派.md)
