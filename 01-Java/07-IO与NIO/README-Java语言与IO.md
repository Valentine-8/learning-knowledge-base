# Java 语言与 IO 深度学习

> **适用人群**：3～7 年 Java 后端工程师，目标从「会用 API」到「能讲原理、能设计、能排障」。  
> **定位**：Phase 1「Java 核心深化」的专题文档，与 [phase1-集合](../phase1-集合/)、[phase2-JVM](../phase2-JVM/)、[phase3-并发](../phase3-并发/) 形成互补。  
> **用法建议**：每章通读 60～90 min → 手写 Demo 验证 → 刷 [05-面试题库与案例](./05-面试题库与案例.md) 对应章节。

---

## 文档导航

| 章节 | 主题 | 核心产出 | 建议时长 |
|------|------|----------|----------|
| [01-面向对象与泛型](./01-面向对象与泛型.md) | OOP 设计、SOLID、泛型与类型擦除 | 能讲清多态调度、PECS、泛型边界 | 90 min |
| [02-注解反射与异常](./02-注解反射与异常.md) | 注解元模型、反射性能、异常体系 | 能解释 Spring/MyBatis 注解原理 | 90 min |
| [03-BIO-NIO与Netty](./03-BIO-NIO与Netty.md) | IO 模型、Selector、Netty 架构 | 能画 Reactor 模型、Pipeline 链路 | 120 min |
| [04-Stream与新特性](./04-Stream与新特性.md) | Stream、Optional、Java 8→21 | 能评估 Parallel Stream 风险 | 90 min |
| [05-面试题库与案例](./05-面试题库与案例.md) | 40+ 高频题 + 线上案例 | 口述 + 白板可复现 | 持续复习 |

---

## 目录（TOC）

### [01-面向对象与泛型](./01-面向对象与泛型.md)

1. 面向对象四大特性与编译期/运行期差异
2. 方法重载 vs 重写、静态绑定 vs 动态绑定
3. 抽象类 vs 接口、Java 8+ 接口演进
4. 组合优于继承：何时继承、何时委托
5. SOLID 原则与后端实战映射
6. 对象相等性：==、equals、hashCode 契约
7. 不可变对象与防御性拷贝
8. 泛型基础：类型参数、边界、通配符
9. PECS 原则与 API 设计
10. 类型擦除：编译后是什么、桥方法、限制
11. 泛型与反射、泛型数组陷阱
12. 常见面试题与 Code Review 清单

### [02-注解反射与异常](./02-注解反射与异常.md)

1. 注解本质：接口 + 元注解
2. 元注解：@Target、@Retention、@Inherited、@Repeatable
3. 注解处理器：编译期 vs 运行期
4. 反射 API：Class、Field、Method、Constructor
5. 反射性能与优化：缓存、MethodHandle、字节码生成
6. Spring 中注解如何变成 Bean：扫描 → 解析 → 注册
7. 异常体系：Checked vs Unchecked
8. 业务异常设计：错误码、国际化、可观测性
9. try-with-resources 与 Suppressed Exception
10. 异常链与「不吞异常」工程规范
11. 全局异常处理与 HTTP 状态码映射
12. 序列化与安全：readObject、反序列化漏洞意识

### [03-BIO-NIO与Netty](./03-BIO-NIO与Netty.md)

1. IO 模型全景：BIO、NIO、AIO、IO 多路复用
2. Java BIO：阻塞点、线程模型、适用场景
3. Java NIO 核心：Buffer、Channel、Selector
4. Reactor 单线程 / 多线程 / 主从模型
5. 零拷贝：sendfile、mmap、Direct Buffer
6. Netty 架构：EventLoop、EventLoopGroup、线程模型
7. ChannelPipeline 与 Handler 责任链
8. ByteBuf：堆内/堆外、引用计数、内存泄漏排查
9. 编解码器与粘包拆包
10. Netty vs Tomcat vs Spring WebFlux 选型
11. 虚拟线程（Java 21）对 IO 编程的影响
12. 线上案例：连接泄漏、慢客户端、Epoll 空轮询

### [04-Stream与新特性](./04-Stream与新特性.md)

1. 函数式接口与 Lambda 本质
2. Stream 操作分类：中间操作 vs 终端操作
3. 惰性求值与短路操作
4. Collectors 高级用法与 groupingBy 陷阱
5. Parallel Stream：ForkJoinPool、线程安全、适用边界
6. Optional 正确使用与反模式
7. java.time 时间 API 与时区处理
8. Java 9～11：模块系统、var、HTTP Client
9. Java 14～17：Record、Sealed Class、Pattern Matching
10. Java 21：Virtual Thread、Structured Concurrency
11. 新特性在业务代码中的落地建议
12. 迁移与兼容性 checklist

### [05-面试题库与案例](./05-面试题库与案例.md)

- **Q1～Q10**：面向对象与泛型
- **Q11～Q20**：注解、反射与异常
- **Q21～Q30**：BIO / NIO / Netty
- **Q31～Q40**：Stream 与 Java 新特性
- **Q41～Q50**：综合设计与线上案例
- 每题含：考点、参考答案、追问、常见踩坑

---

## 与其他 Phase 的关系

```
Java语言与IO（本专题）
    ├─ 前置：Java 语法基础
    ├─ 并行：phase1-集合（数据结构选型）
    ├─ 延伸：phase2-JVM（泛型擦除、反射开销、Direct Memory）
    ├─ 延伸：phase3-并发（NIO + 线程模型、Virtual Thread）
    └─ 应用：phase4-Spring（注解驱动、异常处理、WebFlux）
```

---

## 学习检查清单

- [ ] 能白板画出：多态方法调用解析流程
- [ ] 能解释：`List<? extends Number>` 为何不能 add
- [ ] 能说明：Spring `@Autowired` 与反射的关系
- [ ] 能对比：BIO 一连接一线程 vs Netty Reactor
- [ ] 能列举：Parallel Stream 不适合的 3 类场景
- [ ] 能口述：Record vs 传统 POJO 的取舍
- [ ] 完成 [05-面试题库与案例](./05-面试题库与案例.md) 40+ 题自测

---

← [笔记总览](../../README.md) · [7年技能清单](../../7年Java工程师技能清单.md) · [学习路线](../../7年Java工程师学习路线.md)
