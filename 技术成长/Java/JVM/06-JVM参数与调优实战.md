# 06 · JVM 参数与调优实战

> **目标读者**：7 年 Java 后端，需能配置生产 JVM 参数、解读 GC 日志、针对 Full GC 频繁与延迟高做调优。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 参数分类

| 类型 | 前缀 | 示例 |
|------|------|------|
| 标准 | `-` | `-version`, `-classpath` |
| 非标准（-X） | `-X` | `-Xms`, `-Xmx`, `-Xss` |
| 非稳定（-XX） | `-XX:` | `-XX:+UseG1GC`, `-XX:MaxMetaspaceSize` |

```bash
-XX:+PrintFlagsFinal -version   # 查看默认值
java -XX:+PrintCommandLineFlags -version  # 查看生效参数
```

---

## 2. 堆内存参数

```bash
-Xms4g                          # 初始堆（建议与 Xmx 相同）
-Xmx4g                          # 最大堆
-Xmn1g                          # 新生代（G1 慎用，用 Region 自动）
-XX:NewRatio=2                  # Old:Young = 2:1
-XX:SurvivorRatio=8             # Eden:S0:S1 = 8:1:1
-XX:MaxTenuringThreshold=15     # 晋升年龄阈值
```

| 实践 | 原因 |
|------|------|
| **Xms = Xmx** | 避免运行时扩缩堆，减少 STW |
| 堆不超过物理内存 70% | 留 OS、Metaspace、Direct、栈 |
| 容器内用百分比 | `-XX:MaxRAMPercentage=75.0`（JDK10+） |

```bash
# 容器/K8s 推荐
-XX:InitialRAMPercentage=75.0
-XX:MaxRAMPercentage=75.0
```

---

## 3. Metaspace 与栈

```bash
-XX:MetaspaceSize=256m          # 触发 GC 阈值（非上限）
-XX:MaxMetaspaceSize=512m       # 硬上限，必设
-Xss512k                        # 线程栈（默认约 1M）
-XX:MaxDirectMemorySize=256m    # 直接内存上限
```

---

## 4. G1 调优参数

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=16m
-XX:InitiatingHeapOccupancyPercent=45
-XX:G1ReservePercent=10
-XX:ConcGCThreads=4
```

| 现象 | 调优方向 |
|------|----------|
| Young GC 太频 | 增大堆或 IHOP；检查对象创建速度 |
| Mixed GC 长 | 减少 `-XX:G1MixedGCLiveThresholdPercent` 候选 Region |
| Full GC | **严重**：增大堆、提前并发标记、查泄漏 |
| 停顿超目标 | 降低 MaxGCPauseMillis 期望或增堆 |

---

## 5. ZGC / Parallel 速参

```bash
# ZGC
-XX:+UseZGC
-XX:+ZGenerational

# Parallel 吞吐
-XX:+UseParallelGC
-XX:GCTimeRatio=99
-XX:+UseAdaptiveSizePolicy
```

---

## 6. GC 日志（JDK9+ 统一日志）

```bash
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=50M
-Xlog:safepoint:file=safepoint.log:time,uptime,level,tags
```

### 6.1 关键指标

| 指标 | 健康参考 |
|------|----------|
| Full GC 频率 | 小时/天级，非分钟级 |
| Young GC 耗时 | 通常 <50ms（视堆） |
| GC 时间占比 | <5% 总 CPU 时间 |
| 堆使用率 | Full GC 后老年代应下降 |

### 6.2 JDK8 日志（遗留）

```bash
-XX:+PrintGCDetails -XX:+PrintGCDateStamps
-Xloggc:/path/gc.log
```

---

## 7. OOM 与 Dump 参数

```bash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/heapdump.hprof
-XX:+ExitOnOutOfMemoryError          # K8s 重启 Pod
-XX:OnOutOfMemoryError="kill -9 %p"  # 慎用
```

---

## 8. JIT 与诊断开关

```bash
-XX:+PrintCompilation               # 编译日志（调试）
-XX:ReservedCodeCacheSize=256m      # JIT 代码缓存
-XX:-UseGCOverheadLimit             # 禁用 GC overhead OOM（一般不关）
```

**生产慎用**：`-XX:+TraceClassLoading`、过大 Debug 日志。

---

## 9. 调优实战流程

```
1. 明确目标：吞吐 vs 延迟 vs 内存
2. 基线：GC 日志 + 监控（Prometheus/Grafana）
3. 发现问题：Full GC 频、老年代涨、Metaspace 涨
4. 假设：堆小 / 泄漏 / 大对象 / 参数不当
5. 变更：一次改少量参数，对比 24h
6. 验证：P99 延迟、GC 时间占比、OOM 消失
```

### 案例：老年代持续增长

| 步骤 | 动作 |
|------|------|
| 1 | jstat -gcutil 看 OU 是否只升不降 |
| 2 | Full GC 后 OU 仍高 → 泄漏嫌疑 |
| 3 | dump + MAT |
| 4 | 非泄漏则适当增大堆或 G1 IHOP |

---

## 10. Spring Boot 配置示例

```properties
# application 无法直接设 Xmx，用环境变量或启动脚本
JAVA_OPTS=-Xms2g -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 \
  -XX:MaxMetaspaceSize=256m \
  -XX:+HeapDumpOnOutOfMemoryError \
  -Xlog:gc*:file=gc.log:time,uptime,level,tags
```

---

## 11. 面试要点

| 问 | 答 |
|----|-----|
| Xms 和 Xmx 为什么要相等？ | 避免动态扩缩，性能稳定 |
| MaxGCPauseMillis 能保证吗？ | G1 软目标，非 SLA |
| 如何减少 Full GC？ | 增大堆、修泄漏、G1 并发标记、少 System.gc |
| 容器里如何设堆？ | MaxRAMPercentage，别硬编码超过 cgroup limit |
| System.gc 生产能用吗？ | 别用，可能 Full GC |

---

## 12. 自测

- [ ] 写一套 4G G1 微服务完整参数
- [ ] 解读一条 GC 日志各字段
- [ ] 说明 IHOP 作用

← [05-类加载与双亲委派](./05-类加载与双亲委派.md) · 下一章：[07-诊断工具与OOM排查](./07-诊断工具与OOM排查.md)
