# 7 年 Java 工程师学习路线（详细版）

> **适用人群**：已有 3～5 年 Java 后端经验，目标在 1.5～2 年内达到 **7 年资深工程师** 水平。  
> **学习原则**：每阶段必须有 **产出物**（笔记、Demo、博客、线上案例），拒绝只看视频。  
> **时间投入**：在职每天 2～3 小时 + 周末 1 天，约 **18～24 个月** 走完主线。

---

## 文档导航

| 文档 | 用途 |
|------|------|
| [README.md](../../README.md) | 总入口 |
| [01-7年Java工程师技能清单.md](./01-7年Java工程师技能清单.md) | 技能目标 |
| [02-统一主路线.md](../../00-通用/02-统一主路线.md) | Java + AI 并行时间表 |
| [03-学习进度追踪.md](../../00-通用/03-学习进度追踪.md) | **按 Phase 勾选任务** |
| [12-项目实战清单.md](../../00-通用/12-项目实战清单.md) | Demo 与综合项目 |
| [04-个人基线评估.md](../../00-通用/04-个人基线评估.md) | Phase 0 自评 |
| [notes/](../笔记/) | 分 Phase 笔记 |
| [08-资源书签.md](../../00-通用/08-资源书签.md) | 学习链接 |

---

## 总览路线图

```
Phase 0 基线评估（2 周）
    ↓
Phase 1 Java 核心深化（8 周）
    ↓
Phase 2 JVM 与性能（8 周）
    ↓
Phase 3 并发与高性能 IO（6 周）
    ↓
Phase 4 Spring 生态源码级理解（8 周）
    ↓
Phase 5 数据库与缓存（8 周）
    ↓
Phase 6 分布式与中间件（10 周）
    ↓
Phase 7 架构设计与工程化（8 周）
    ↓
Phase 8 云原生与 DevOps（6 周）
    ↓
Phase 9 综合项目与面试/晋升（持续）
```

---

## Phase 0：基线评估（第 1～2 周）

### 目标
摸清差距，制定个人优先级，避免重复学习。

### 具体任务

| 天 | 任务 | 产出 |
|----|------|------|
| D1 | 做《7年Java工程师技能清单》自评，每项 1～5 分 | 自评表格 |
| D2 | LeetCode 热题 10 道（数组/哈希），限时完成 | 正确率记录 |
| D3 | 手写：ArrayList 扩容、LRU（LinkedHashMap）、生产者消费者 | 3 个可运行 Demo |
| D4 | 线上案例：用 jstack + MAT 分析一次 OOM 或 Full GC（可用本地模拟） | 排查报告 1 篇 |
| D5 | Spring：画 IoC 容器启动流程 + 一次 HTTP 请求全链路 | 手绘/Excalidraw 图 |
| D6 | MySQL：explain 分析 5 条业务 SQL，写出优化建议 | SQL 优化文档 |
| D7 | 制定个人学习计划：标红弱项，调整 Phase 顺序 | 个人版路线 |

### 推荐资源
- 自评对照：[01-7年Java工程师技能清单.md](./01-7年Java工程师技能清单.md)
- 算法：LeetCode Hot 100 列表

---

## Phase 1：Java 核心深化（第 3～10 周）

### 目标
从「会用」到「能讲原理 + 能写高质量代码」，覆盖面试与 Code Review 场景。

### 第 1～2 周：集合 + 泛型 + 反射

**学习内容**
1. HashMap：JDK7 头插 vs JDK8 尾插、树化阈值、resize 过程
2. ConcurrentHashMap：JDK7 Segment vs JDK8 synchronized+CAS
3. ArrayList vs LinkedList vs ArrayDeque 选型
4. 泛型擦除、`<extends T>` vs `<super T>`（PECS）
5. 反射性能问题、MethodHandle 了解

**每日安排（示例）**
- 工作日：1h 源码阅读（OpenJDK / 本地 IDE）+ 0.5h 笔记
- 周末：4h 手写简化版 HashMap + 单元测试

**必读**
- 《Java 核心技术 卷 I》第 9～12 章
- 文章：JavaGuide 集合框架源码专题

**产出**
- [ ] 博客：《HashMap 扩容与线程安全》
- [ ] GitHub：`mini-hashmap` 项目（put/get/resize）

**验收**
- 能白板画出 HashMap put 全流程
- 能回答：为什么 HashMap 线程不安全？ConcurrentHashMap 如何保证并发？

---

### 第 3～4 周：Stream + 时间 API + 新特性

**学习内容**
1. Stream 中间操作/终止操作、惰性求值
2. Parallel Stream 适用场景与坑（ForkJoinPool）
3. `java.time`：Instant、ZonedDateTime、Duration
4. Java 17：Record、Sealed Class、Pattern Matching for switch
5. Java 21：Virtual Thread 入门（Project Loom）

**实战**
- 用 Stream 重构一段 legacy for 循环代码
- 写一个 Virtual Thread 对比 Platform Thread 的 HTTP 压测 Demo

**产出**
- [ ] 代码：业务模块 Stream 重构 PR（或本地 Demo）

---

### 第 5～6 周：IO + NIO 基础

**学习内容**
1. BIO 阻塞模型
2. NIO：Buffer、Channel、Selector 多路复用
3. 零拷贝（sendfile、mmap）
4. Netty 入门：Reactor 模型、Bootstrap 写 Echo Server

**推荐**
- 《Netty 实战》第 1～5 章
- 视频：尚硅谷 Netty 前 20 集（可选）

**产出**
- [ ] Demo：NIO 多客户端聊天室 或 Netty Echo Server

---

### 第 7～8 周：设计模式（结合业务）

**学习内容**
不在背 23 种，重点掌握 8 种高频：
- 单例（枚举 / 静态内部类）
- 工厂 / 抽象工厂
- 策略 + 模板方法
- 装饰器（IO 流、Spring 包装）
- 代理（静态 / JDK / CGLIB）
- 观察者（Spring Event）
- 责任链（Filter、Interceptor）
- 建造者（Lombok @Builder、复杂对象构建）

**实战**
- 用策略模式重构 if-else 业务分支
- 用责任链实现审批流 Demo

**产出**
- [ ] 博客：《项目中真正用到的 6 种设计模式》

---

## Phase 2：JVM 与性能（第 11～18 周）

### 目标
能独立做 JVM 调优、OOM 排查，理解 GC 选型依据。

### 第 1～2 周：内存模型与 GC 基础

**学习内容**
1. 堆（Eden/S0/S1/Old）、栈、MetaSpace、直接内存
2. 对象头、指针压缩
3. GC 算法：标记清除/复制/标记整理
4. 收集器：Serial、Parallel、CMS（了解淘汰原因）、**G1**、**ZGC**

**实验**
```bash
# 本地启动 Java 进程，观察 GC
java -Xms512m -Xmx512m -XX:+UseG1GC -Xlog:gc* -jar your-app.jar
```

**必读**
- 《深入理解 Java 虚拟机（第 3 版）》第 2～3 章
- 官方：Oracle G1 GC Tuning Guide

**产出**
- [ ] 笔记：各 GC 对比表（停顿、吞吐、堆大小适用）

---

### 第 3～4 周：类加载 + 字节码

**学习内容**
1. 加载 → 验证 → 准备 → 解析 → 初始化
2. 双亲委派与 SPI（ServiceLoader）
3. 自定义 ClassLoader 场景
4. javap 反编译字节码，理解 synthetics

**实验**
- 写自定义 ClassLoader 加载加密 class 文件

**产出**
- [ ] Demo：`EncryptedClassLoader`

---

### 第 5～6 周：调优实战

**学习内容**
1. 常用参数：`-Xms/-Xmx`、`-XX:MaxMetaspaceSize`、G1 的 `-XX:MaxGCPauseMillis`
2. jps、jstat、jmap、jstack 组合拳
3. MAT：Dominator Tree、GC Roots、Leak Suspects
4. Arthas：dashboard、thread、watch、trace

**实验**
1. 故意制造内存泄漏（静态集合持有大对象）
2. 用 MAT 找到泄漏点
3. 用 Arthas trace 慢方法

**产出**
- [ ] 博客：《一次 Full GC 频繁的排查实录》（可模拟）

---

### 第 7～8 周：JIT + 性能分析

**学习内容**
1. 热点编译、逃逸分析、栈上分配
2. async-profiler 火焰图
3. JFR（Java Flight Recorder）
4. 微基准测试 JMH 入门

**产出**
- [ ] 一次火焰图分析记录 + 优化前后对比数据

**验收**
- 给定 OOM dump，30 分钟内定位可疑对象
- 说出 G1 和 ZGC 选型场景

---

## Phase 3：并发与高性能（第 19～24 周）

### 目标
精通 JUC，能设计线程安全的高并发模块。

### 第 1～2 周：并发基础

**学习内容**
1. happens-before 规则
2. synchronized 锁升级（偏向→轻量→重量）
3. volatile 语义与 DCL 单例
4. CAS 与 ABA 问题

**必读**
- 《Java 并发编程的艺术》第 2～5 章

---

### 第 3～4 周：JUC 深入

**学习内容**
1. AQS 原理（CLH 队列、state）
2. ReentrantLock vs synchronized
3. Semaphore、CountDownLatch、CyclicBarrier 使用场景
4. ConcurrentHashMap 分段锁演进
5. CopyOnWriteArrayList、BlockingQueue 家族

**源码阅读顺序**
`AbstractQueuedSynchronizer` → `ReentrantLock` → `ThreadPoolExecutor`

---

### 第 5～6 周：线程池 + 异步

**学习内容**
1. 7 参数含义，队列选型（ArrayBlocking vs Linked vs Synchronous）
2. 拒绝策略与 CallerRuns 的妙用
3. 线程池监控指标（活跃线程、队列长度、拒绝次数）
4. CompletableFuture 编排
5. `@Async` 与线程池隔离

**实战**
- 搭建动态线程池 Demo（参考美团 DynamicTp 思路）
- 压测：错误配置线程池导致 OOM 或拒绝

**产出**
- [ ] 博客：《线程池参数如何按业务估算》
- [ ] 可配置线程池组件（集成到 Spring Boot）

**验收**
- 手写简易线程池（核心功能：任务提交、工作线程、阻塞队列）
- 解释：为什么 Executors 工厂方法不推荐？

---

## Phase 4：Spring 生态源码级理解（第 25～32 周）

### 目标
从使用者变为「能改框架、能排坑」的 Spring 开发者。

### 第 1～2 周：Spring Core

**源码阅读路径**
1. `@Configuration` + `@Bean` 注册流程
2. Bean 生命周期（Instantiation → Populate → Initialize → Destroy）
3. 循环依赖：三级缓存
4. `@Autowired` 注入原理

**推荐**
- 《Spring 核心技术内幕》或 程序员鱼皮 Spring 源码系列

**产出**
- [ ] 手绘：Bean 生命周期 + 循环依赖解决图

---

### 第 3～4 周：Spring Boot + 自动配置

**学习内容**
1. `@SpringBootApplication` 三注解
2. `spring.factories` / `AutoConfiguration.imports`
3. `@ConditionalOnClass` 等条件装配
4. Starter 自定义：写 `my-spring-boot-starter`

**实战**
- 自定义 Starter：统一日志 / 统一异常处理 / 限流注解

**产出**
- [ ] GitHub：`my-spring-boot-starter`

---

### 第 5～6 周：Spring MVC + 事务

**学习内容**
1. DispatcherServlet 请求分发
2. HandlerMapping、HandlerAdapter、ViewResolver
3. 拦截器 vs Filter 顺序
4. `@Transactional` 失效场景（同类调用、非 public、异常类型）
5. 事务传播行为 7 种，能举业务例子

**实验**
- 构造 5 种事务失效 Case 并验证

---

### 第 7～8 周：Spring Cloud 微服务

**学习内容（选 Spring Cloud Alibaba 或 Spring Cloud Netflix 其一）**
1. Nacos 注册发现 + 配置中心
2. OpenFeign / Dubbo RPC
3. Gateway 路由与过滤器
4. Sentinel 限流熔断
5. Seata 分布式事务（AT 模式 Demo）

**实战项目骨架**
```
order-service / inventory-service / payment-service
+ Gateway + Nacos + Sentinel + Seata
```

**产出**
- [ ] 微服务 Demo：下单扣库存（含 Seata 或本地消息表）

**验收**
- 能讲一次 Feign 调用全链路
- 能配置 Sentinel 规则并解释滑动窗口

---

## Phase 5：数据库与缓存（第 33～40 周）

### 目标
SQL 优化到索引级别，Redis 用到集群与分布式锁生产级。

### 第 1～3 周：MySQL 深度

**学习内容**
1. InnoDB 架构：Buffer Pool、Redo Log、Undo Log、Binlog
2. 索引：B+ 树、聚簇/非聚簇、覆盖索引、索引下推
3. 执行计划 type、key、rows、Extra 字段
4. 锁：行锁、间隙锁、Next-Key Lock
5. MVCC：Read View、快照读 vs 当前读
6. 慢 SQL 优化流程

**必读**
- 《MySQL 必知必会》+ 《高性能 MySQL》第 4～7 章

**实验**
- 建表 100 万行，对比有/无索引查询
- 模拟幻读，验证 RR 级别下间隙锁

**产出**
- [ ] 博客：《5 条真实 SQL 的优化过程》

---

### 第 4～5 周：分库分表

**学习内容**
1. 垂直拆分 vs 水平拆分
2. ShardingSphere-JDBC 配置
3. 分布式 ID：雪花算法、号段模式
4. 跨库 Join、分页、排序问题

**实战**
- ShardingSphere 分 2 库 4 表 Demo

---

### 第 6～8 周：Redis 深度

**学习内容**
1. 5 种基础类型 + 3 种特殊（Bitmap、HyperLogLog、GEO）
2. 持久化 RDB vs AOF、混合持久化
3. 主从复制、哨兵、Cluster 槽位
4. 缓存穿透/击穿/雪崩解决方案
5. 分布式锁：Redisson 看门狗、RedLock 争议
6. 缓存与 DB 一致性：Cache Aside、延迟双删

**必读**
- 《Redis 设计与实现》
- Redis 官方文档 Persistence / Cluster 章节

**实战**
- 实现：秒杀接口（Redis 预减库存 + Lua 脚本 + 异步落库）
- 实现：Redisson 分布式锁 + 业务 Demo

**产出**
- [ ] 博客：《缓存一致性方案在生产中的取舍》
- [ ] Demo：seckill-redis 项目

**验收**
- 手写 Redis 分布式锁（SET NX PX + Lua 释放）
- 解释 Cluster MOVED/ASK 重定向

---

## Phase 6：分布式与中间件（第 41～50 周）

### 目标
理解分布式系统核心问题，至少精通 Kafka 或 RocketMQ 之一。

### 第 1～2 周：分布式理论

**学习内容**
1. CAP、BASE
2. Paxos/Raft 了解（能讲 Raft 选举）
3. 一致性哈希
4. 分布式 ID、分布式 Session

**推荐**
- 《数据密集型应用系统设计（DDIA）》第 5～9 章（精读）

---

### 第 3～5 周：消息队列（以 Kafka 为例）

**学习内容**
1. Topic、Partition、Consumer Group
2. 消息顺序、重复消费、丢失场景
3. 幂等生产、事务消息
4. 积压排查与扩容
5. RocketMQ 对比：延迟消息、事务消息

**实战**
- 订单系统：下单发 MQ → 库存服务消费 → 死信队列
- 实现幂等消费（唯一键 / Redis Set）

**产出**
- [ ] 博客：《Kafka 消息不丢的三层保障》

---

### 第 6～7 周：Elasticsearch

**学习内容**
1. 倒排索引原理
2. Mapping、Analyzer
3. 聚合查询、分页 deep paging 问题
4. 数据同步：Canal / Logstash

**实战**
- 商品搜索 Demo：MySQL → ES 同步 + 多条件搜索

---

### 第 8～10 周：分布式事务与 Seata

**学习内容**
1. 2PC/3PC 问题
2. TCC、Saga 适用场景
3. 本地消息表、最大努力通知
4. Seata AT 模式原理（ undo_log ）

**实战**
- 微服务 Demo 接入 Seata AT
- 或手写 TCC 简易版（Try/Confirm/Cancel 三接口）

**验收**
- 画出 TCC 与 AT 的流程对比图
- 说出你的业务适合哪种分布式事务方案

---

## Phase 7：架构设计与工程化（第 51～58 周）

### 目标
能独立输出技术方案，具备 Tech Lead 能力。

### 第 1～2 周：DDD 入门

**学习内容**
1. 战略设计：限界上下文、上下文映射
2. 战术设计：实体、值对象、聚合根、领域服务、领域事件
3. 充血模型 vs 贫血模型

**推荐**
- 《领域驱动设计精粹》
-  COLA 架构示例（阿里开源）

**实战**
- 选一个业务域（订单/用户）做 DDD 建模文档

---

### 第 3～4 周：系统设计方法论

**学习内容**
1. 需求澄清 → 容量估算 → 架构图 → 核心流程 → 数据模型 → 风险点
2. 高可用：限流、熔断、降级、多活
3. 典型系统设计：短链、Feed、秒杀、IM

**练习（每题 2h 限时）**
- 设计一个支持 10 万 QPS 的秒杀系统
- 设计一个分布式定时任务系统

**产出**
- [ ] 2 篇系统设计文档（含 QPS 估算过程）

---

### 第 5～6 周：Code Review 与规范

**学习内容**
1. 阿里巴巴 Java 开发手册（精读）
2. Clean Code 核心原则
3. SonarQube 规则
4. 单元测试：JUnit5 + Mockito，覆盖率有意义的模块

**实践**
- 制定团队 Java 编码规范 1 份
- 给开源项目或同事代码做 3 次 Review 记录

---

### 第 7～8 周：技术方案写作

**学习内容**
1. ADR（Architecture Decision Record）模板
2. 技术方案结构：背景、目标、方案对比、风险、排期
3. 故障复盘文档：时间线、根因、改进项

**产出**
- [ ] 1 份完整技术方案（可虚构：引入 Kafka 替换同步调用）
- [ ] 1 份故障复盘（可基于历史或模拟）

---

## Phase 8：云原生与 DevOps（第 59～64 周）

### 目标
应用能容器化部署到 K8s，具备完整 CI/CD 与可观测性意识。

### 第 1～2 周：Linux + Docker

**学习内容**
1. 常用命令：top、vmstat、iostat、netstat/ss、tcpdump
2. Dockerfile 最佳实践（多阶段构建、非 root 用户）
3. docker-compose 本地编排

**实战**
- Spring Boot 应用 Docker 化，镜像体积优化到 200MB 以内

---

### 第 3～4 周：Kubernetes

**学习内容**
1. Pod、Deployment、Service、ConfigMap、Secret
2. Ingress、HPA
3. 健康检查 liveness/readiness
4. 滚动更新与回滚

**实战**
- minikube 或 Kind 本地集群部署 Phase 4 微服务 Demo
- 配置 ConfigMap 外置配置

**推荐**
- 《Kubernetes in Action》前 10 章
- 官方 Tutorial：kubectl basics

---

### 第 5～6 周：CI/CD + 可观测性

**学习内容**
1. GitLab CI / GitHub Actions 流水线：构建 → 测试 → 镜像 → 部署
2. Prometheus + Grafana：JVM 指标、业务指标
3. SkyWalking / Jaeger 链路追踪
4. ELK 或 Loki 日志查询

**实战**
- 为 Demo 项目配置完整 CI/CD + Grafana 大盘

**产出**
- [ ] 可运行的 `docker-compose` 或 K8s yaml + CI 配置

**验收**
- 从 git push 到服务自动部署全流程跑通
- 能在 Grafana 看到 RT、QPS、错误率

---

## Phase 9：综合项目与职业跃迁（持续）

### 综合实战项目（选 1 个做深）

#### 项目 A：电商交易链路（推荐）
| 模块 | 技术点 |
|------|--------|
| 用户/商品 | Spring Boot + MyBatis + Redis 缓存 |
| 订单 | 分库分表 + 分布式 ID |
| 库存 | Redis 预扣 + MQ 异步 + 幂等 |
| 支付 | 模拟回调 + 本地消息表 |
| 搜索 | ES 同步 |
| 网关 | Gateway + Sentinel |
| 部署 | Docker + K8s + CI/CD |
| 观测 | Prometheus + SkyWalking |

#### 项目 B：实时数据平台
Kafka + Flink + Redis + MySQL，侧重流处理与大数据方向。

#### 项目 C：开源贡献
选 Spring / ShardingSphere / RocketMQ 等提 PR，哪怕文档或小 bug fix。

### 算法维持（每周 3～5 题）
- 重点：哈希、链表、二叉树、二分、滑动窗口、BFS/DFS、DP 入门
- 目标：LeetCode 累计 200+，Hot 100 二刷通过率 80%+

### 面试/晋升准备（4～6 周冲刺）

| 周 | 重点 |
|----|------|
| W1 | Java 基础 + 集合 + 并发：每天 10 道面试题自讲录音 |
| W2 | JVM + MySQL + Redis：结合项目经历整理 STAR 故事 |
| W3 | Spring + 微服务 + MQ：画架构图脱稿讲 30 分钟 |
| W4 | 系统设计 2 题 + 算法每日 2 题 |
| W5 | 模拟面试 + 薄弱点回补 |
| W6 | 真实面试 or 晋升答辩材料 |

**STAR 故事准备（至少 5 个）**
1. 一次性能优化（有数据）
2. 一次线上故障排查
3. 一次技术选型/架构升级
4. 一次带新人/Review 提效
5. 一次跨团队协作推动上线

---

## 推荐书单（按优先级）

| 优先级 | 书名 | 对应 Phase |
|--------|------|------------|
| P0 | 《深入理解 Java 虚拟机》 | Phase 2 |
| P0 | 《Java 并发编程的艺术》 | Phase 3 |
| P0 | 《高性能 MySQL》 | Phase 5 |
| P0 | 《Redis 设计与实现》 | Phase 5 |
| P1 | 《Spring 核心技术内幕》 | Phase 4 |
| P1 | 《数据密集型应用系统设计 DDIA》 | Phase 6 |
| P1 | 《领域驱动设计精粹》 | Phase 7 |
| P2 | 《Netty 实战》 | Phase 1 |
| P2 | 《Kubernetes in Action》 | Phase 8 |
| P2 | 《阿里巴巴 Java 开发手册》 | Phase 7 |

---

## 在线资源

| 类型 | 资源 |
|------|------|
| 综合 | [JavaGuide](https://javaguide.cn/)、[CyC2018/CS-Notes](https://github.com/CyC2018/CS-Notes) |
| 源码 | [Spring 源码系列](https://www.iocoder.cn/categories/04-Spring/) |
| 算法 | LeetCode Hot 100、代码随想录 |
| 系统设计 | bytebytego、System Design Primer |
| 工具 | Arthas 官方文档、ShardingSphere 官方文档 |
| 英文 | Baeldung、Spring 官方 Reference |

---

## 学习节奏建议

### 在职工程师一周模板

| 时段 | 内容 |
|------|------|
| 周一～周五 7:00～8:00 | 算法 1～2 题 |
| 周一～周五 20:30～22:30 | 主线课程/源码/实验 |
| 周六 | 项目实战 6h |
| 周日 | 复习笔记 + 博客输出 3h，休息 |

### 里程碑检查点

| 时间点 | 应达到状态 |
|--------|------------|
| 3 个月 | HashMap/JUC 源码能讲；完成 JVM OOM 排查实验 |
| 6 个月 | Spring 循环依赖、事务能讲；MySQL 索引优化熟练 |
| 9 个月 | Redis + Kafka Demo 完成；微服务骨架跑通 |
| 12 个月 | 综合项目 MVP 上线（本地/K8s） |
| 18 个月 | 系统设计能独立输出；具备 Senior 面试通过率 |
| 24 个月 | 综合项目完善 + 1～2 篇高质量技术博客 + 晋升/跳槽就绪 |

---

## 常见误区（务必避免）

1. **只看不练**：JVM、并发、MySQL 必须动手实验  
2. **追框架不追原理**：新框架年年出，原理 10 年不变  
3. **算法临时抱佛脚**：200 题是长期积累，不是冲刺 2 周  
4. **忽视软技能**：7 年工程师差距往往在方案、沟通、复盘  
5. **完美主义**：Demo 能跑、能讲清楚即可，不追求生产完美  
6. **孤立学习**：加入技术社群、做分享，教是最好的学  

---

## 与现有笔记的衔接

[notes/phase1-集合/01-ArrayList.md](../笔记/phase1-集合/01-ArrayList.md) 已有 ArrayList 源码分析，建议：
1. 按 Phase 1 补齐 HashMap、ConcurrentHashMap 同等深度笔记（见 [notes/phase1-集合/](../笔记/phase1-集合/)）  
2. DevOps 见 Phase 8 与 [notes/phase8-DevOps/](../笔记/phase8-DevOps/)  
3. 每完成 Phase，更新 [04-个人基线评估.md](../../00-通用/04-个人基线评估.md) 与 [03-学习进度追踪.md](../../00-通用/03-学习进度追踪.md)  

---

## 附录：每日学习记录模板

```markdown
## 日期：YYYY-MM-DD

### 今日目标
- [ ] 

### 学习内容（链接/章节）
- 

### 代码/实验
- 

### 问题与待查
- 

### 明日计划
- 
```

坚持记录 6 个月，复习效率会提升 3 倍以上。
