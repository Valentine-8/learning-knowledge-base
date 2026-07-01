# 07 · 诊断工具与 OOM 排查

> **目标读者**：7 年 Java 后端，需能使用 jps/jstat/jmap/jstack、MAT、Arthas 完成线上 OOM 与 CPU 高、死锁排查。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. JDK 自带命令行工具

| 工具 | 用途 | 常用命令 |
|------|------|----------|
| **jps** | 列 Java 进程 | `jps -lvm` |
| **jstat** | GC/类加载统计 | `jstat -gcutil <pid> 1000 10` |
| **jinfo** | 查看/改部分参数 | `jinfo -flags <pid>` |
| **jmap** | 堆 dump / 摘要 | `jmap -heap <pid>` |
| **jstack** | 线程栈 | `jstack -l <pid>` |
| **jcmd** | 综合诊断 | `jcmd <pid> GC.heap_info` |

---

## 2. jstat 读 GC

```bash
jstat -gcutil 12345 1000
```

| 列 | 含义 |
|----|------|
| S0/S1/E | Survivor、Eden 使用率 % |
| O | 老年代 |
| M | Metaspace |
| YGC/YGCT | Young GC 次数/总耗时 |
| FGC/FGCT | Full GC 次数/总耗时 |
| GCT | GC 总时间 |

**诊断**：FGC 频繁且 O 接近 100% → 泄漏或堆不足；M 持续涨 → Metaspace/类加载问题。

---

## 3. jmap 与 Heap Dump

```bash
#  live 对象，减小文件
jmap -dump:live,format=b,file=heap.hprof <pid>

# jcmd 等价（推荐，更安全）
jcmd <pid> GC.heap_dump /tmp/heap.hprof
```

| 注意 | 说明 |
|------|------|
| dump 会 STW | 大堆选低峰；生产优先 `live` |
| 文件大小 | 接近堆占用，预留磁盘 |
| 多次 dump | 对比 Dominator 增长对象 |

```bash
jmap -histo:live <pid> | head -30   # 对象实例数 Top
```

---

## 4. jstack 与线程问题

```bash
jstack -l <pid> > thread.txt
```

| 场景 | 线程栈特征 |
|------|------------|
| 死锁 | `Found one Java-level deadlock` |
| CPU 高 | 某 Runnable 线程栈重复出现 |
| 阻塞 | `BLOCKED` on monitor |
| 等待 | `WAITING` / `TIMED_WAITING` |

**CPU 高排查**：

```bash
top -Hp <pid>              # 找高 CPU 线程 tid
printf "%x\n" tid          # 转 16 进制
jstack <pid> | grep <hex>  # 定位栈
```

---

## 5. MAT（Memory Analyzer Tool）

### 5.1 核心视图

| 视图 | 用途 |
|------|------|
| **Leak Suspects** | 自动泄漏嫌疑报告 |
| **Dominator Tree** | 谁 retained 最多堆 |
| **Histogram** | 按类统计实例与 shallow heap |
| **GC Roots** | 到对象的引用链 |

### 5.2 分析流程

```
1. 打开 hprof
2. Leak Suspects / Dominator Tree Top
3. 右键 → Path to GC Roots（exclude weak）
4. 找到业务代码持有链（静态 Map、ThreadLocal、缓存）
5. 对比两次 dump 的 Dominator 差异
```

**Retained Heap**：对象被回收能释放的总大小（含仅被它引用的子对象）。

---

## 6. Arthas（在线诊断）

```bash
java -jar arthas-boot.jar
```

| 命令 | 用途 |
|------|------|
| `dashboard` | 线程、内存、GC 概览 |
| `thread -n 3` | CPU 最高 3 线程 |
| `jvm` | JVM 信息 |
| `memory` | 内存分布 |
| `heapdump /tmp/d.hprof` | 在线 dump |
| `watch com.app.Service method '{params,returnObj}' -x 2` | 观察入参返回值 |
| `trace com.app.Service method` | 调用耗时分解 |
| `stack com.app.Service method` | 谁调用了方法 |
| `profiler start` | 火焰图（async-profiler） |

**优势**：不停机、Attach 运行中进程。

---

## 7. OOM 类型与排查

| OOM 信息 | 方向 |
|----------|------|
| `Java heap space` | dump → MAT；查缓存、集合、ThreadLocal |
| `Metaspace` | 类加载过多；CGLib 代理；设 MaxMetaspaceSize |
| `Direct buffer memory` | Netty/NIO；泄漏 DirectBuffer |
| `unable to create new native thread` | 线程过多；`-Xss` 或减线程 |
| `GC overhead limit exceeded` | 98% GC 回收 <2%；堆太小或泄漏 |

### 7.1 标准排查流程

```
1. 确认 OOM 类型（日志 / -XX:+HeapDumpOnOOM）
2. 保留现场：hprof + gc.log + 应用日志
3. MAT Dominator + Leak Suspects
4. GC Roots 链到代码
5. 修复：有界缓存、remove 监听器、WeakReference
6. 压测验证 + 监控告警
```

---

## 8. Full GC 频繁排查

```
jstat -gcutil → FGC 增、O 高
     ├─ Full GC 后 O 降 → 堆可能偏小，适当增大
     └─ Full GC 后 O 仍高 → 内存泄漏
              → 两次 dump 对比
              → 查 ThreadLocal、静态集合、连接池未关
```

---

## 9. async-profiler 火焰图

```bash
# CPU
profiler start
profiler stop --format html > cpu.html

# 内存分配
profiler start --event alloc
```

定位热点方法与分配大户。

---

## 10. 面试要点

| 问 | 答 |
|----|-----|
| 如何排查 OOM？ | 类型 → dump → MAT Dominator → GC Roots → 修代码 |
| jstack 用途？ | 死锁、阻塞、CPU 高线程栈 |
| jmap 注意？ | STW；live 减小体积 |
| MAT Dominator Tree？ | 最大 retained 对象，找泄漏根 |
| Arthas 和 MAT 区别？ | Arthas 在线；MAT 离线分析 dump |

---

## 11. 自测

- [ ] 模拟堆 OOM 并用 MAT 找 Leak Suspects
- [ ] 用 jstat 判断泄漏 vs 堆小
- [ ] 写 Arthas trace 一条慢接口

← [06-JVM参数与调优实战](./06-JVM参数与调优实战.md) · 下一章：[08-生产案例与面试题库](./08-生产案例与面试题库.md)
