# Repository Structure

> 本文档定义 Java 全栈工程师知识库的长期目录蓝图。目录按知识体系分类，而不是按学习阶段分类。本文档中的文件代表未来规划清单，实际创建可分阶段进行；未创建文件不得被正式文档引用为已存在内容。

## 1. 顶层结构

```text
.
├── README.md
├── Repository-Specification.md
├── Repository-Structure.md
├── 00-Governance/
├── 技术成长/Java/
├── 02-Spring-Ecosystem/
├── 03-Database/
├── 技术成长/数据与中间件/Redis/
├── 技术成长/数据与中间件/消息队列/
├── 06-Middleware/
├── 07-Microservices/
├── 08-JVM/
├── 09-Concurrency/
├── 10-Distributed-Systems/
├── 11-Architecture/
├── 12-Linux/
├── 13-Docker/
├── 14-Kubernetes/
├── 15-DevOps/
├── 16-Computer-Science/
├── 17-Frontend/
├── 技术成长/AI工程/
├── 技术成长/C++嵌入式/
├── 20-Project-Practice/
├── 技术成长/00-通用/
├── 技术成长/00-通用/
├── 98-Personal-Topics/
├── 99-Archive/
└── assets/
```

## 2. 00-Governance

```text
00-Governance/
├── README.md
├── 01-Repository-Specification.md
├── 02-Repository-Structure.md
├── 03-Markdown-Style-Guide.md
├── 04-README-Template.md
├── 05-Technical-Article-Template.md
├── 06-Migration-Guide.md
├── 07-AI-Writing-Checklist.md
├── 08-Link-Check-Guide.md
├── 09-Image-Asset-Guide.md
├── 10-Mermaid-Guide.md
├── 11-Code-Example-Guide.md
├── 12-Quality-Acceptance-Checklist.md
├── 13-Content-Lifecycle.md
├── 14-Codex-Cursor-Workflow.md
└── 03-Learning-Roadmaps/
    ├── README.md
    ├── 01-Java-Backend-Roadmap.md
    ├── 02-Java-Fullstack-Roadmap.md
    ├── 03-Architect-Roadmap.md
    ├── 04-AI-Engineering-Roadmap.md
    ├── 05-Frontend-Roadmap.md
    └── 06-Interview-Roadmap.md
```

## 3. 01-Java

```text
技术成长/Java/
├── README.md
├── 01-语言基础/
│   ├── README.md
│   ├── 01-Java语言概览.md
│   ├── 02-JDK-JRE-JVM.md
│   ├── 03-基本数据类型.md
│   ├── 04-运算符与表达式.md
│   ├── 05-流程控制.md
│   ├── 06-数组.md
│   ├── 07-字符串.md
│   ├── 08-枚举.md
│   ├── 09-包与访问控制.md
│   └── 10-编码规范.md
├── 02-面向对象/
│   ├── README.md
│   ├── 01-类与对象.md
│   ├── 02-封装.md
│   ├── 03-继承.md
│   ├── 04-多态.md
│   ├── 05-抽象类.md
│   ├── 06-接口.md
│   ├── 07-内部类.md
│   ├── 08-对象创建与初始化.md
│   └── 09-面向对象设计原则.md
├── 03-集合框架/
│   ├── README.md
│   ├── 01-集合框架总览.md
│   ├── 02-ArrayList.md
│   ├── 03-LinkedList.md
│   ├── 04-Vector.md
│   ├── 05-HashMap.md
│   ├── 06-LinkedHashMap.md
│   ├── 07-TreeMap.md
│   ├── 08-HashSet.md
│   ├── 09-TreeSet.md
│   ├── 10-Iterator.md
│   ├── 11-Comparable与Comparator.md
│   ├── 12-集合扩容机制.md
│   ├── 13-集合线程安全.md
│   └── 14-集合框架面试题.md
├── 04-泛型/
│   ├── README.md
│   ├── 01-泛型基础.md
│   ├── 02-类型擦除.md
│   ├── 03-通配符.md
│   ├── 04-泛型方法.md
│   ├── 05-泛型边界.md
│   └── 06-泛型最佳实践.md
├── 05-异常处理/
│   ├── README.md
│   ├── 01-异常体系.md
│   ├── 02-Checked与Unchecked异常.md
│   ├── 03-try-catch-finally.md
│   ├── 04-try-with-resources.md
│   ├── 05-自定义异常.md
│   └── 06-异常处理实践.md
├── 06-注解与反射/
│   ├── README.md
│   ├── 01-注解基础.md
│   ├── 02-元注解.md
│   ├── 03-反射基础.md
│   ├── 04-反射调用机制.md
│   ├── 05-动态代理.md
│   ├── 06-JDK代理与CGLIB.md
│   └── 07-反射性能与安全.md
├── 07-IO与NIO/
│   ├── README.md
│   ├── 01-IO模型总览.md
│   ├── 02-字节流与字符流.md
│   ├── 03-缓冲流.md
│   ├── 04-序列化.md
│   ├── 05-NIO-Buffer.md
│   ├── 06-NIO-Channel.md
│   ├── 07-NIO-Selector.md
│   ├── 08-AIO.md
│   └── 09-Netty入门关联.md
├── 08-Lambda与Stream/
│   ├── README.md
│   ├── 01-Lambda表达式.md
│   ├── 02-函数式接口.md
│   ├── 03-方法引用.md
│   ├── 04-Stream基础.md
│   ├── 05-Stream中间操作.md
│   ├── 06-Stream终止操作.md
│   ├── 07-Optional.md
│   └── 08-Stream性能与陷阱.md
└── 09-新版本特性/
    ├── README.md
    ├── 01-Java8核心特性.md
    ├── 02-Java11核心特性.md
    ├── 03-Java17核心特性.md
    ├── 04-Java21核心特性.md
    ├── 05-Record.md
    ├── 06-Sealed-Class.md
    ├── 07-Pattern-Matching.md
    └── 08-Virtual-Threads关联.md
```

## 4. 02-Spring-Ecosystem

```text
02-Spring-Ecosystem/
├── README.md
├── 01-Spring-Framework/
│   ├── README.md
│   ├── 01-Spring体系总览.md
│   ├── 02-IoC容器.md
│   ├── 03-Bean生命周期.md
│   ├── 04-依赖注入.md
│   ├── 05-AOP原理.md
│   ├── 06-事务管理.md
│   ├── 07-事件机制.md
│   ├── 08-资源加载.md
│   └── 09-Spring源码阅读路径.md
├── 02-Spring-Boot/
│   ├── README.md
│   ├── 01-SpringBoot总览.md
│   ├── 02-自动配置原理.md
│   ├── 03-启动流程.md
│   ├── 04-配置体系.md
│   ├── 05-Starter机制.md
│   ├── 06-Actuator.md
│   ├── 07-外部化配置.md
│   ├── 08-SpringBoot3迁移.md
│   └── 09-生产部署实践.md
├── 03-Spring-MVC/
│   ├── README.md
│   ├── 01-MVC请求流程.md
│   ├── 02-DispatcherServlet.md
│   ├── 03-Controller设计.md
│   ├── 04-参数绑定.md
│   ├── 05-数据校验.md
│   ├── 06-异常处理.md
│   ├── 07-拦截器.md
│   └── 08-RESTful接口设计.md
├── 04-Spring-Security/
│   ├── README.md
│   ├── 01-认证与授权总览.md
│   ├── 02-过滤器链.md
│   ├── 03-用户名密码认证.md
│   ├── 04-JWT认证.md
│   ├── 05-OAuth2.md
│   ├── 06-方法级权限.md
│   └── 07-安全配置实践.md
├── 05-Spring-Data/
│   ├── README.md
│   ├── 01-Spring-JDBC.md
│   ├── 02-Spring-Data-JPA.md
│   ├── 03-MyBatis集成.md
│   ├── 04-MyBatis-Plus.md
│   ├── 05-事务失效场景.md
│   └── 06-读写分离实践.md
├── 06-Spring-Cloud/
│   ├── README.md
│   ├── 01-SpringCloud总览.md
│   ├── 02-服务注册与发现.md
│   ├── 03-配置中心.md
│   ├── 04-OpenFeign.md
│   ├── 05-Gateway.md
│   ├── 06-负载均衡.md
│   ├── 07-熔断限流.md
│   ├── 08-链路追踪.md
│   └── 09-SpringCloudAlibaba.md
└── 07-Spring-AI/
    ├── README.md
    ├── 01-Spring-AI总览.md
    ├── 02-ChatClient.md
    ├── 03-Prompt模板.md
    ├── 04-Embedding.md
    ├── 05-VectorStore.md
    ├── 06-Function-Calling.md
    └── 07-RAG实践.md
```

## 5. 03-Database

```text
03-Database/
├── README.md
├── 01-数据库基础/
│   ├── README.md
│   ├── 01-数据库系统概览.md
│   ├── 02-关系模型.md
│   ├── 03-SQL基础.md
│   ├── 04-范式与反范式.md
│   ├── 05-事务基础.md
│   └── 06-数据库设计规范.md
├── 02-MySQL/
│   ├── README.md
│   ├── 01-MySQL架构总览.md
│   ├── 02-InnoDB存储引擎.md
│   ├── 03-Buffer-Pool.md
│   ├── 04-Redo-Log.md
│   ├── 05-Undo-Log.md
│   ├── 06-Binlog.md
│   ├── 07-B+树索引.md
│   ├── 08-聚簇索引与二级索引.md
│   ├── 09-覆盖索引.md
│   ├── 10-索引失效.md
│   ├── 11-事务隔离级别.md
│   ├── 12-MVCC.md
│   ├── 13-锁机制.md
│   ├── 14-死锁分析.md
│   ├── 15-EXPLAIN.md
│   ├── 16-SQL优化.md
│   ├── 17-主从复制.md
│   ├── 18-高可用方案.md
│   ├── 19-分库分表.md
│   ├── 20-分布式ID.md
│   └── 21-MySQL生产案例.md
├── 03-PostgreSQL/
│   ├── README.md
│   ├── 01-PostgreSQL总览.md
│   ├── 02-数据类型.md
│   ├── 03-索引体系.md
│   ├── 04-MVCC.md
│   ├── 05-执行计划.md
│   ├── 06-JSONB.md
│   ├── 07-扩展机制.md
│   └── 08-运维实践.md
├── 04-SQL优化/
│   ├── README.md
│   ├── 01-SQL优化方法论.md
│   ├── 02-慢查询分析.md
│   ├── 03-索引设计.md
│   ├── 04-分页优化.md
│   ├── 05-Join优化.md
│   ├── 06-批量写入优化.md
│   └── 07-数据库性能排查.md
└── 05-数据库面试/
    ├── README.md
    ├── 01-MySQL高频面试题.md
    ├── 02-事务与锁面试题.md
    ├── 03-索引面试题.md
    └── 04-SQL优化面试题.md
```

## 6. 04-Redis

```text
技术成长/数据与中间件/Redis/
├── README.md
├── 01-Redis基础/
│   ├── README.md
│   ├── 01-Redis总览.md
│   ├── 02-单线程模型.md
│   ├── 03-网络模型.md
│   ├── 04-内存模型.md
│   └── 05-键过期与淘汰策略.md
├── 02-数据结构/
│   ├── README.md
│   ├── 01-String.md
│   ├── 02-List.md
│   ├── 03-Hash.md
│   ├── 04-Set.md
│   ├── 05-ZSet.md
│   ├── 06-Bitmap.md
│   ├── 07-HyperLogLog.md
│   ├── 08-Geo.md
│   └── 09-Stream.md
├── 03-持久化与高可用/
│   ├── README.md
│   ├── 01-RDB.md
│   ├── 02-AOF.md
│   ├── 03-主从复制.md
│   ├── 04-Sentinel.md
│   ├── 05-Cluster.md
│   └── 06-故障转移.md
├── 04-缓存设计/
│   ├── README.md
│   ├── 01-缓存模式.md
│   ├── 02-缓存穿透.md
│   ├── 03-缓存击穿.md
│   ├── 04-缓存雪崩.md
│   ├── 05-热点Key.md
│   ├── 06-大Key治理.md
│   └── 07-缓存一致性.md
├── 05-并发与分布式锁/
│   ├── README.md
│   ├── 01-SETNX分布式锁.md
│   ├── 02-Redisson.md
│   ├── 03-RedLock.md
│   ├── 04-限流.md
│   └── 05-幂等控制.md
└── 06-生产实践/
    ├── README.md
    ├── 01-Redis性能优化.md
    ├── 02-Redis监控.md
    ├── 03-Redis故障排查.md
    ├── 04-Redis面试题.md
    └── 05-Redis生产案例.md
```

## 7. 05-Message-Queue

```text
技术成长/数据与中间件/消息队列/
├── README.md
├── 01-消息队列基础/
│   ├── README.md
│   ├── 01-消息队列总览.md
│   ├── 02-消息模型.md
│   ├── 03-可靠性语义.md
│   ├── 04-顺序消息.md
│   ├── 05-延迟消息.md
│   ├── 06-死信队列.md
│   └── 07-MQ选型.md
├── 02-Kafka/
│   ├── README.md
│   ├── 01-Kafka架构.md
│   ├── 02-Topic与Partition.md
│   ├── 03-Producer.md
│   ├── 04-Consumer.md
│   ├── 05-Consumer-Group.md
│   ├── 06-Offset管理.md
│   ├── 07-副本机制.md
│   ├── 08-Exactly-Once.md
│   ├── 09-Kafka性能优化.md
│   └── 10-Kafka生产案例.md
├── 03-RabbitMQ/
│   ├── README.md
│   ├── 01-RabbitMQ架构.md
│   ├── 02-Exchange.md
│   ├── 03-Queue.md
│   ├── 04-Routing-Key.md
│   ├── 05-可靠投递.md
│   ├── 06-消费确认.md
│   └── 07-RabbitMQ生产实践.md
├── 04-RocketMQ/
│   ├── README.md
│   ├── 01-RocketMQ架构.md
│   ├── 02-NameServer.md
│   ├── 03-Broker.md
│   ├── 04-Producer.md
│   ├── 05-Consumer.md
│   ├── 06-事务消息.md
│   ├── 07-顺序消息.md
│   └── 08-RocketMQ生产实践.md
└── 05-消息队列面试/
    ├── README.md
    ├── 01-MQ高频面试题.md
    ├── 02-Kafka面试题.md
    ├── 03-RabbitMQ面试题.md
    └── 04-RocketMQ面试题.md
```

## 8. 06-Middleware

```text
06-Middleware/
├── README.md
├── 01-Elasticsearch/
│   ├── README.md
│   ├── 01-Elasticsearch总览.md
│   ├── 02-倒排索引.md
│   ├── 03-Mapping.md
│   ├── 04-写入流程.md
│   ├── 05-查询流程.md
│   ├── 06-聚合查询.md
│   ├── 07-集群架构.md
│   ├── 08-性能优化.md
│   └── 09-生产案例.md
├── 02-Netty/
│   ├── README.md
│   ├── 01-Netty总览.md
│   ├── 02-Reactor模型.md
│   ├── 03-Channel.md
│   ├── 04-EventLoop.md
│   ├── 05-ByteBuf.md
│   ├── 06-编解码器.md
│   └── 07-Netty实战.md
├── 03-Nginx/
│   ├── README.md
│   ├── 01-Nginx总览.md
│   ├── 02-反向代理.md
│   ├── 03-负载均衡.md
│   ├── 04-静态资源.md
│   ├── 05-HTTPS配置.md
│   └── 06-Nginx生产实践.md
├── 04-注册配置中心/
│   ├── README.md
│   ├── 01-Nacos.md
│   ├── 02-Consul.md
│   ├── 03-Etcd.md
│   └── 04-配置中心实践.md
└── 05-API网关/
    ├── README.md
    ├── 01-网关职责.md
    ├── 02-Spring-Cloud-Gateway.md
    ├── 03-认证鉴权.md
    ├── 04-限流熔断.md
    └── 05-网关生产实践.md
```

## 9. 07-Microservices

```text
07-Microservices/
├── README.md
├── 01-微服务基础/
│   ├── README.md
│   ├── 01-微服务架构总览.md
│   ├── 02-单体到微服务.md
│   ├── 03-服务拆分原则.md
│   ├── 04-服务边界.md
│   ├── 05-接口契约.md
│   └── 06-微服务治理模型.md
├── 02-服务治理/
│   ├── README.md
│   ├── 01-注册发现.md
│   ├── 02-负载均衡.md
│   ├── 03-限流.md
│   ├── 04-熔断.md
│   ├── 05-降级.md
│   ├── 06-重试.md
│   └── 07-超时控制.md
├── 03-可观测性/
│   ├── README.md
│   ├── 01-日志体系.md
│   ├── 02-指标监控.md
│   ├── 03-链路追踪.md
│   ├── 04-告警治理.md
│   └── 05-SLO与SLI.md
└── 04-发布与演进/
    ├── README.md
    ├── 01-灰度发布.md
    ├── 02-蓝绿发布.md
    ├── 03-金丝雀发布.md
    ├── 04-版本兼容.md
    └── 05-微服务故障复盘.md
```

## 10. 08-JVM

```text
08-JVM/
├── README.md
├── 01-JVM基础/
│   ├── README.md
│   ├── 01-JVM总览.md
│   ├── 02-运行时数据区.md
│   ├── 03-对象内存布局.md
│   ├── 04-对象创建过程.md
│   └── 05-直接内存.md
├── 02-类加载/
│   ├── README.md
│   ├── 01-类加载过程.md
│   ├── 02-类加载器.md
│   ├── 03-双亲委派模型.md
│   ├── 04-SPI机制.md
│   └── 05-类加载问题排查.md
├── 03-垃圾回收/
│   ├── README.md
│   ├── 01-GC总览.md
│   ├── 02-可达性分析.md
│   ├── 03-垃圾回收算法.md
│   ├── 04-Serial与Parallel.md
│   ├── 05-CMS.md
│   ├── 06-G1.md
│   ├── 07-ZGC.md
│   ├── 08-Shenandoah.md
│   └── 09-GC日志分析.md
├── 04-性能调优/
│   ├── README.md
│   ├── 01-JVM参数.md
│   ├── 02-内存溢出分析.md
│   ├── 03-CPU飙高分析.md
│   ├── 04-线程Dump分析.md
│   ├── 05-HeapDump分析.md
│   ├── 06-JFR.md
│   └── 07-JVM调优案例.md
└── 05-JVM面试/
    ├── README.md
    ├── 01-JVM高频面试题.md
    ├── 02-GC面试题.md
    └── 03-类加载面试题.md
```

## 11. 09-Concurrency

```text
09-Concurrency/
├── README.md
├── 01-并发基础/
│   ├── README.md
│   ├── 01-进程与线程.md
│   ├── 02-线程生命周期.md
│   ├── 03-上下文切换.md
│   ├── 04-线程安全.md
│   ├── 05-可见性原子性有序性.md
│   └── 06-Java内存模型.md
├── 02-锁与同步/
│   ├── README.md
│   ├── 01-synchronized.md
│   ├── 02-锁升级.md
│   ├── 03-volatile.md
│   ├── 04-ReentrantLock.md
│   ├── 05-ReadWriteLock.md
│   ├── 06-StampedLock.md
│   ├── 07-CAS.md
│   └── 08-AQS.md
├── 03-JUC工具类/
│   ├── README.md
│   ├── 01-CountDownLatch.md
│   ├── 02-CyclicBarrier.md
│   ├── 03-Semaphore.md
│   ├── 04-Exchanger.md
│   ├── 05-LockSupport.md
│   └── 06-CompletableFuture.md
├── 04-线程池/
│   ├── README.md
│   ├── 01-ThreadPoolExecutor.md
│   ├── 02-线程池参数.md
│   ├── 03-拒绝策略.md
│   ├── 04-任务队列.md
│   ├── 05-线程池监控.md
│   └── 06-线程池生产实践.md
├── 05-并发容器/
│   ├── README.md
│   ├── 01-ConcurrentHashMap.md
│   ├── 02-CopyOnWriteArrayList.md
│   ├── 03-BlockingQueue.md
│   ├── 04-ConcurrentLinkedQueue.md
│   └── 05-DelayQueue.md
└── 06-并发面试/
    ├── README.md
    ├── 01-JUC高频面试题.md
    ├── 02-线程池面试题.md
    └── 03-锁机制面试题.md
```

## 12. 10-Distributed-Systems

```text
10-Distributed-Systems/
├── README.md
├── 01-分布式基础/
│   ├── README.md
│   ├── 01-分布式系统总览.md
│   ├── 02-CAP.md
│   ├── 03-BASE.md
│   ├── 04-一致性模型.md
│   ├── 05-分布式时钟.md
│   └── 06-故障模型.md
├── 02-一致性协议/
│   ├── README.md
│   ├── 01-Paxos.md
│   ├── 02-Raft.md
│   ├── 03-ZAB.md
│   ├── 04-Gossip.md
│   └── 05-一致性协议对比.md
├── 03-分布式事务/
│   ├── README.md
│   ├── 01-二阶段提交.md
│   ├── 02-三阶段提交.md
│   ├── 03-TCC.md
│   ├── 04-Saga.md
│   ├── 05-本地消息表.md
│   ├── 06-事务消息.md
│   └── 07-Seata.md
├── 04-分布式工程问题/
│   ├── README.md
│   ├── 01-分布式ID.md
│   ├── 02-幂等设计.md
│   ├── 03-重复请求.md
│   ├── 04-分布式锁.md
│   ├── 05-限流.md
│   ├── 06-数据一致性.md
│   └── 07-最终一致性实践.md
└── 05-分布式面试/
    ├── README.md
    ├── 01-分布式高频面试题.md
    ├── 02-分布式事务面试题.md
    └── 03-一致性协议面试题.md
```

## 13. 11-Architecture

```text
11-Architecture/
├── README.md
├── 01-架构基础/
│   ├── README.md
│   ├── 01-架构设计总览.md
│   ├── 02-架构目标.md
│   ├── 03-质量属性.md
│   ├── 04-架构权衡.md
│   ├── 05-架构评审.md
│   └── 06-技术选型.md
├── 02-设计模式/
│   ├── README.md
│   ├── 01-设计模式总览.md
│   ├── 02-单例模式.md
│   ├── 03-工厂模式.md
│   ├── 04-建造者模式.md
│   ├── 05-代理模式.md
│   ├── 06-策略模式.md
│   ├── 07-模板方法模式.md
│   ├── 08-观察者模式.md
│   └── 09-责任链模式.md
├── 03-DDD/
│   ├── README.md
│   ├── 01-DDD总览.md
│   ├── 02-领域与子域.md
│   ├── 03-限界上下文.md
│   ├── 04-实体与值对象.md
│   ├── 05-聚合.md
│   ├── 06-领域服务.md
│   ├── 07-领域事件.md
│   └── 08-DDD落地实践.md
├── 04-高并发架构/
│   ├── README.md
│   ├── 01-高并发架构方法论.md
│   ├── 02-缓存架构.md
│   ├── 03-异步化.md
│   ├── 04-削峰填谷.md
│   ├── 05-限流降级.md
│   ├── 06-热点治理.md
│   └── 07-容量评估.md
├── 05-高可用架构/
│   ├── README.md
│   ├── 01-高可用设计.md
│   ├── 02-容灾设计.md
│   ├── 03-故障隔离.md
│   ├── 04-降级预案.md
│   ├── 05-演练机制.md
│   └── 06-故障复盘.md
└── 06-系统设计/
    ├── README.md
    ├── 01-系统设计方法论.md
    ├── 02-短链系统设计.md
    ├── 03-秒杀系统设计.md
    ├── 04-订单系统设计.md
    ├── 05-支付系统设计.md
    ├── 06-IM系统设计.md
    └── 07-推荐系统设计.md
```

## 14. 12-Linux

```text
12-Linux/
├── README.md
├── 01-Linux基础/
│   ├── README.md
│   ├── 01-Linux系统总览.md
│   ├── 02-文件系统.md
│   ├── 03-用户与权限.md
│   ├── 04-进程管理.md
│   ├── 05-服务管理.md
│   └── 06-软件包管理.md
├── 02-Shell/
│   ├── README.md
│   ├── 01-Shell基础.md
│   ├── 02-变量与参数.md
│   ├── 03-管道与重定向.md
│   ├── 04-文本处理.md
│   ├── 05-脚本编写.md
│   └── 06-Shell实践.md
├── 03-网络排查/
│   ├── README.md
│   ├── 01-ip.md
│   ├── 02-ss.md
│   ├── 03-netstat.md
│   ├── 04-curl.md
│   ├── 05-tcpdump.md
│   └── 06-网络故障排查案例.md
└── 04-性能分析/
    ├── README.md
    ├── 01-top与htop.md
    ├── 02-vmstat.md
    ├── 03-iostat.md
    ├── 04-sar.md
    ├── 05-perf.md
    └── 06-Linux性能排查方法论.md
```

## 15. 13-Docker

```text
13-Docker/
├── README.md
├── 01-Docker基础/
│   ├── README.md
│   ├── 01-Docker总览.md
│   ├── 02-镜像.md
│   ├── 03-容器.md
│   ├── 04-Dockerfile.md
│   ├── 05-数据卷.md
│   └── 06-Docker网络.md
├── 02-镜像构建/
│   ├── README.md
│   ├── 01-多阶段构建.md
│   ├── 02-镜像瘦身.md
│   ├── 03-构建缓存.md
│   ├── 04-安全扫描.md
│   └── 05-Java应用镜像.md
└── 03-Docker-Compose/
    ├── README.md
    ├── 01-Compose基础.md
    ├── 02-本地开发环境.md
    ├── 03-多服务编排.md
    └── 04-Compose实践.md
```

## 16. 14-Kubernetes

```text
14-Kubernetes/
├── README.md
├── 01-Kubernetes基础/
│   ├── README.md
│   ├── 01-Kubernetes总览.md
│   ├── 02-集群架构.md
│   ├── 03-Pod.md
│   ├── 04-Deployment.md
│   ├── 05-Service.md
│   ├── 06-Ingress.md
│   └── 07-Namespace.md
├── 02-配置与存储/
│   ├── README.md
│   ├── 01-ConfigMap.md
│   ├── 02-Secret.md
│   ├── 03-Volume.md
│   ├── 04-PersistentVolume.md
│   └── 05-StorageClass.md
├── 03-调度与伸缩/
│   ├── README.md
│   ├── 01-调度器.md
│   ├── 02-亲和性.md
│   ├── 03-污点与容忍.md
│   ├── 04-HPA.md
│   └── 05-资源限制.md
└── 04-生产实践/
    ├── README.md
    ├── 01-滚动更新.md
    ├── 02-健康检查.md
    ├── 03-可观测性.md
    ├── 04-故障排查.md
    └── 05-Java应用部署.md
```

## 17. 15-DevOps

```text
15-DevOps/
├── README.md
├── 01-Git/
│   ├── README.md
│   ├── 01-Git基础.md
│   ├── 02-分支模型.md
│   ├── 03-提交规范.md
│   ├── 04-冲突处理.md
│   └── 05-Git工作流.md
├── 02-CI-CD/
│   ├── README.md
│   ├── 01-CICD总览.md
│   ├── 02-GitHub-Actions.md
│   ├── 03-Jenkins.md
│   ├── 04-流水线设计.md
│   ├── 05-质量门禁.md
│   └── 06-发布回滚.md
├── 03-可观测性/
│   ├── README.md
│   ├── 01-日志平台.md
│   ├── 02-Prometheus.md
│   ├── 03-Grafana.md
│   ├── 04-OpenTelemetry.md
│   └── 05-告警治理.md
└── 04-环境治理/
    ├── README.md
    ├── 01-开发环境.md
    ├── 02-测试环境.md
    ├── 03-预发环境.md
    ├── 04-生产环境.md
    └── 05-配置与密钥管理.md
```

## 18. 16-Computer-Science

```text
16-Computer-Science/
├── README.md
├── 01-数据结构与算法/
│   ├── README.md
│   ├── 01-复杂度分析.md
│   ├── 02-数组.md
│   ├── 03-链表.md
│   ├── 04-栈与队列.md
│   ├── 05-哈希表.md
│   ├── 06-树.md
│   ├── 07-堆.md
│   ├── 08-图.md
│   ├── 09-排序算法.md
│   ├── 10-二分查找.md
│   ├── 11-递归与回溯.md
│   ├── 12-动态规划.md
│   ├── 13-贪心算法.md
│   └── 14-LeetCode题型总结.md
├── 02-操作系统/
│   ├── README.md
│   ├── 01-操作系统总览.md
│   ├── 02-进程与线程.md
│   ├── 03-进程调度.md
│   ├── 04-内存管理.md
│   ├── 05-虚拟内存.md
│   ├── 06-文件系统.md
│   ├── 07-IO模型.md
│   └── 08-死锁.md
├── 03-计算机网络/
│   ├── README.md
│   ├── 01-网络模型.md
│   ├── 02-TCP.md
│   ├── 03-UDP.md
│   ├── 04-HTTP.md
│   ├── 05-HTTPS.md
│   ├── 06-DNS.md
│   ├── 07-从URL到页面.md
│   ├── 08-网络排查.md
│   └── 09-网络面试题.md
├── 04-计算机组成/
│   ├── README.md
│   ├── 01-计算机组成总览.md
│   ├── 02-CPU.md
│   ├── 03-内存.md
│   ├── 04-缓存.md
│   ├── 05-指令.md
│   └── 06-存储.md
└── 05-安全基础/
    ├── README.md
    ├── 01-Web攻击与防护.md
    ├── 02-认证授权.md
    ├── 03-OAuth2.md
    ├── 04-JWT.md
    ├── 05-加密基础.md
    └── 06-API安全.md
```

## 19. 17-Frontend

```text
17-Frontend/
├── README.md
├── 01-HTML/
│   ├── README.md
│   ├── 01-HTML基础.md
│   ├── 02-语义化标签.md
│   ├── 03-表单.md
│   └── 04-可访问性基础.md
├── 02-CSS/
│   ├── README.md
│   ├── 01-CSS基础.md
│   ├── 02-盒模型.md
│   ├── 03-Flex.md
│   ├── 04-Grid.md
│   ├── 05-响应式布局.md
│   └── 06-CSS工程化.md
├── 03-JavaScript/
│   ├── README.md
│   ├── 01-JavaScript基础.md
│   ├── 02-作用域与闭包.md
│   ├── 03-原型与继承.md
│   ├── 04-异步编程.md
│   ├── 05-Promise.md
│   ├── 06-事件循环.md
│   └── 07-模块化.md
├── 04-TypeScript/
│   ├── README.md
│   ├── 01-TypeScript基础.md
│   ├── 02-类型系统.md
│   ├── 03-泛型.md
│   ├── 04-工具类型.md
│   └── 05-TypeScript工程实践.md
├── 05-Vue3/
│   ├── README.md
│   ├── 01-Vue3总览.md
│   ├── 02-组合式API.md
│   ├── 03-响应式原理.md
│   ├── 04-组件通信.md
│   ├── 05-Vue-Router.md
│   ├── 06-Pinia.md
│   ├── 07-性能优化.md
│   └── 08-Vue3项目实践.md
├── 06-Nodejs/
│   ├── README.md
│   ├── 01-Nodejs总览.md
│   ├── 02-模块系统.md
│   ├── 03-包管理.md
│   ├── 04-文件系统.md
│   └── 05-服务端基础.md
└── 07-工程化/
    ├── README.md
    ├── 01-Vite.md
    ├── 02-Webpack.md
    ├── 03-ESLint.md
    ├── 04-Prettier.md
    ├── 05-前端测试.md
    └── 06-前端部署.md
```

## 20. 18-AI-Engineering

```text
技术成长/AI工程/
├── README.md
├── 01-AI工程基础/
│   ├── README.md
│   ├── 01-AI工程总览.md
│   ├── 02-LLM基础概念.md
│   ├── 03-Token与上下文窗口.md
│   ├── 04-模型能力边界.md
│   └── 05-AI应用架构.md
├── 02-Prompt-Engineering/
│   ├── README.md
│   ├── 01-Prompt基础.md
│   ├── 02-角色与任务设计.md
│   ├── 03-结构化输出.md
│   ├── 04-多轮对话设计.md
│   └── 05-Prompt评测.md
├── 03-LLM-API/
│   ├── README.md
│   ├── 01-LLM-API集成.md
│   ├── 02-流式输出.md
│   ├── 03-结构化响应.md
│   ├── 04-错误处理.md
│   ├── 05-成本控制.md
│   └── 06-Java集成实践.md
├── 04-RAG/
│   ├── README.md
│   ├── 01-RAG总览.md
│   ├── 02-文档切分.md
│   ├── 03-Embedding.md
│   ├── 04-向量数据库.md
│   ├── 05-检索增强.md
│   ├── 06-Rerank.md
│   ├── 07-RAG评测.md
│   └── 08-RAG生产实践.md
├── 05-Agent/
│   ├── README.md
│   ├── 01-Agent总览.md
│   ├── 02-Function-Calling.md
│   ├── 03-Tool-Use.md
│   ├── 04-Memory.md
│   ├── 05-规划与执行.md
│   └── 06-Agent安全边界.md
├── 06-MCP/
│   ├── README.md
│   ├── 01-MCP协议总览.md
│   ├── 02-MCP-Server.md
│   ├── 03-MCP-Client.md
│   ├── 04-Tool设计.md
│   └── 05-MCP工程实践.md
├── 07-模型部署与微调/
│   ├── README.md
│   ├── 01-本地模型部署.md
│   ├── 02-推理优化.md
│   ├── 03-LoRA微调.md
│   ├── 04-模型量化.md
│   └── 05-部署成本评估.md
└── 08-AI安全与评测/
    ├── README.md
    ├── 01-AI安全总览.md
    ├── 02-Prompt-Injection.md
    ├── 03-数据泄露风险.md
    ├── 04-模型评测.md
    ├── 05-可观测性.md
    └── 06-合规与治理.md
```

## 21. 19-Cpp

```text
技术成长/C++嵌入式/
├── README.md
├── 01-Cpp基础/
│   ├── README.md
│   ├── 01-Cpp语言总览.md
│   ├── 02-编译与链接.md
│   ├── 03-类型系统.md
│   ├── 04-指针与引用.md
│   ├── 05-内存管理.md
│   └── 06-面向对象.md
├── 02-STL/
│   ├── README.md
│   ├── 01-STL总览.md
│   ├── 02-vector.md
│   ├── 03-list.md
│   ├── 04-map.md
│   ├── 05-unordered_map.md
│   ├── 06-迭代器.md
│   └── 07-算法库.md
├── 03-现代Cpp/
│   ├── README.md
│   ├── 01-Cpp11核心特性.md
│   ├── 02-智能指针.md
│   ├── 03-移动语义.md
│   ├── 04-Lambda.md
│   ├── 05-并发编程.md
│   └── 06-RAII.md
├── 04-嵌入式/
│   ├── README.md
│   ├── 01-嵌入式系统总览.md
│   ├── 02-交叉编译.md
│   ├── 03-内存与寄存器.md
│   ├── 04-中断.md
│   ├── 05-RTOS.md
│   └── 06-嵌入式调试.md
└── 05-从Java到Cpp/
    ├── README.md
    ├── 01-语言模型差异.md
    ├── 02-内存模型差异.md
    ├── 03-工程构建差异.md
    └── 04-迁移学习路线.md
```

## 22. 20-Project-Practice

```text
20-Project-Practice/
├── README.md
├── 01-项目方法论/
│   ├── README.md
│   ├── 01-项目实战学习法.md
│   ├── 02-需求分析.md
│   ├── 03-技术方案设计.md
│   ├── 04-数据库设计.md
│   ├── 05-接口设计.md
│   └── 06-上线与复盘.md
├── 02-电商系统/
│   ├── README.md
│   ├── 01-电商系统总览.md
│   ├── 02-商品系统.md
│   ├── 03-库存系统.md
│   ├── 04-订单系统.md
│   ├── 05-支付系统.md
│   ├── 06-优惠券系统.md
│   └── 07-秒杀系统.md
├── 03-SaaS系统/
│   ├── README.md
│   ├── 01-SaaS架构总览.md
│   ├── 02-租户模型.md
│   ├── 03-权限模型.md
│   ├── 04-数据隔离.md
│   └── 05-计费系统.md
├── 04-内容系统/
│   ├── README.md
│   ├── 01-CMS系统设计.md
│   ├── 02-搜索系统.md
│   ├── 03-推荐系统.md
│   └── 04-审核系统.md
├── 05-AI应用项目/
│   ├── README.md
│   ├── 01-知识库问答系统.md
│   ├── 02-智能客服系统.md
│   ├── 03-代码助手系统.md
│   └── 04-Agent工作流系统.md
└── 06-故障复盘案例/
    ├── README.md
    ├── 01-数据库慢查询故障.md
    ├── 02-Redis缓存雪崩故障.md
    ├── 03-MQ消息堆积故障.md
    ├── 04-JVM内存溢出故障.md
    └── 05-Kubernetes发布故障.md
```

## 23. 21-Interview

```text
技术成长/00-通用/
├── README.md
├── 01-面试方法论/
│   ├── README.md
│   ├── 01-面试准备总览.md
│   ├── 02-技术表达结构.md
│   ├── 03-项目讲解方法.md
│   ├── 04-追问应对.md
│   └── 05-面试复盘.md
├── 02-Java面试/
│   ├── README.md
│   ├── 01-Java基础面试题.md
│   ├── 02-集合面试题.md
│   ├── 03-JVM面试题.md
│   ├── 04-JUC面试题.md
│   └── 05-Spring面试题.md
├── 03-数据库面试/
│   ├── README.md
│   ├── 01-MySQL面试题.md
│   ├── 02-Redis面试题.md
│   ├── 03-MQ面试题.md
│   └── 04-Elasticsearch面试题.md
├── 04-架构面试/
│   ├── README.md
│   ├── 01-系统设计面试题.md
│   ├── 02-微服务面试题.md
│   ├── 03-分布式面试题.md
│   └── 04-高并发面试题.md
├── 05-项目面试/
│   ├── README.md
│   ├── 01-项目经历组织.md
│   ├── 02-项目亮点.md
│   ├── 03-项目难点.md
│   ├── 04-项目复盘.md
│   └── 05-项目追问题库.md
└── 06-简历与求职/
    ├── README.md
    ├── 01-简历结构.md
    ├── 02-项目描述.md
    ├── 03-技能描述.md
    ├── 04-求职追踪.md
    └── 05-Offer选择.md
```

## 24. 90-Growth

```text
技术成长/00-通用/
├── README.md
├── 01-学习方法/
│   ├── README.md
│   ├── 01-技术学习方法.md
│   ├── 02-阅读源码方法.md
│   ├── 03-做项目的方法.md
│   ├── 04-复盘方法.md
│   └── 05-错题本方法.md
├── 02-工程素养/
│   ├── README.md
│   ├── 01-代码质量.md
│   ├── 02-文档能力.md
│   ├── 03-排查能力.md
│   ├── 04-沟通协作.md
│   └── 05-技术判断.md
├── 03-职业发展/
│   ├── README.md
│   ├── 01-工程师能力模型.md
│   ├── 02-高级工程师成长.md
│   ├── 03-架构师成长.md
│   ├── 04-技术管理入门.md
│   └── 05-长期主义.md
└── 04-个人模板/
    ├── README.md
    ├── 01-周复盘模板.md
    ├── 02-学习计划模板.md
    ├── 03-项目复盘模板.md
    ├── 04-面试复盘模板.md
    └── 05-阅读笔记模板.md
```

## 25. 98-Personal-Topics

```text
98-Personal-Topics/
├── README.md
└── Photography/
    ├── README.md
    └── Olympus-EP7/
        ├── README.md
        ├── 01-第一次拿到EP7.md
        ├── 02-认识EP7.md
        ├── 03-第一次开机设置.md
        ├── 04-模式转盘.md
        ├── 05-14-42EZ镜头.md
        ├── 06-40-150R镜头.md
        ├── 07-第一次出去拍照.md
        ├── 08-拍人像.md
        ├── 09-拍风景.md
        ├── 10-夜景.md
        ├── 11-菜单详解.md
        ├── 12-常见问题.md
        ├── 13-RAW后期入门.md
        ├── 14-视频与Vlog.md
        ├── 15-旅行摄影.md
        ├── 16-术语表.md
        └── images/
```

## 26. 99-Archive

```text
99-Archive/
├── README.md
├── Legacy-Technical-Growth/
│   ├── README.md
│   ├── 技术成长原目录说明.md
│   └── old-files/
├── Frontend-Demos/
│   ├── README.md
│   └── Vue2-Basic/
│       ├── README.md
│       ├── 01helloworld/
│       ├── 02数据绑定/
│       ├── 03数据代理/
│       ├── 04事件处理/
│       ├── 05计算属性/
│       ├── 06监听属性/
│       ├── js/
│       └── VUE/
├── Old-Roadmaps/
│   ├── README.md
│   ├── 学习路线.md
│   └── 学习路线-旧版.md
└── Raw-Migrations/
    ├── README.md
    ├── Java-Phase-Notes/
    ├── Data-Middleware-Notes/
    ├── AI-Engineering-Notes/
    ├── Computer-Science-Notes/
    └── Cpp-Embedded-Notes/
```

## 27. assets

```text
assets/
├── README.md
├── images/
│   ├── README.md
│   ├── java/
│   ├── spring/
│   ├── database/
│   ├── redis/
│   ├── message-queue/
│   ├── middleware/
│   ├── microservices/
│   ├── jvm/
│   ├── concurrency/
│   ├── distributed-systems/
│   ├── architecture/
│   ├── linux/
│   ├── docker/
│   ├── kubernetes/
│   ├── devops/
│   ├── computer-science/
│   ├── frontend/
│   ├── ai-engineering/
│   ├── cpp/
│   └── personal/
├── diagrams/
│   ├── README.md
│   ├── source/
│   └── exported/
├── screenshots/
│   ├── README.md
│   ├── tools/
│   └── cases/
└── examples/
    ├── README.md
    ├── java/
    ├── spring/
    ├── database/
    ├── redis/
    ├── mq/
    ├── frontend/
    └── ai-engineering/
```

## 28. 现有内容迁移映射

现有目录不应直接删除。第二阶段迁移时按以下映射处理。

| 现有位置 | 目标位置 | 处理方式 |
|---|---|---|
| `技术成长/Java/笔记/phase1-集合/` | `技术成长/Java/笔记/phase1-集合/` | 拆分、重命名、补齐章节 |
| `08-JVM/01-JVM基础/` | `08-JVM/` | 按 JVM 模块迁移 |
| `09-Concurrency/01-并发基础/` | `09-Concurrency/` | 按 JUC、线程池、锁拆分 |
| `02-Spring-Ecosystem/01-Spring-Framework/` | `02-Spring-Ecosystem/` | 按 Spring 子项目迁移 |
| `03-Database/01-数据库基础/` | `03-Database/` | 与 MySQL 内容合并去重 |
| `10-Distributed-Systems/01-分布式基础/` | `10-Distributed-Systems/` | 按一致性、事务、工程问题迁移 |
| `11-Architecture/01-架构基础/` | `11-Architecture/` | 按架构主题迁移 |
| `15-DevOps/01-Git与协作/` | `15-DevOps/` | 按 Git、CI/CD、环境治理迁移 |
| `技术成长/数据与中间件/MySQL/` | `技术成长/数据与中间件/MySQL/` | 复用深度内容并规范文件名 |
| `技术成长/数据与中间件/Redis/` | `技术成长/数据与中间件/Redis/` | 复用并补齐生产实践 |
| `技术成长/数据与中间件/消息队列/` | `技术成长/数据与中间件/消息队列/` | 按 Kafka、RocketMQ、通用 MQ 拆分 |
| `技术成长/数据与中间件/Elasticsearch/` | `技术成长/数据与中间件/Elasticsearch/` | 迁移并补齐集群与性能 |
| `16-Computer-Science/` | `16-Computer-Science/` | 按算法、网络、OS、安全迁移 |
| `技术成长/AI工程/` | `技术成长/AI工程/` | 按 Prompt、RAG、Agent、MCP 拆分 |
| `技术成长/C++嵌入式/` | `技术成长/C++嵌入式/`、`技术成长/00-通用/` | 技术内容与求职内容分离 |
| `前端/vue/` | `前端/vue/` | 保留历史 Demo，不作为正式 Vue3 知识 |
| `奥林巴斯ep7/EP7-Guide/` | `奥林巴斯ep7/EP7-Guide/` | 保留个人摄影专题 |
| `技术成长/00-通用/` | `技术成长/00-通用/`、`技术成长/00-通用/`、`99-Archive/` | 按成长、面试、归档拆分 |

## 29. 分阶段落地顺序

第一阶段只创建并确认：

```text
Repository-Specification.md
Repository-Structure.md
```

第二阶段建立骨架：

```text
README.md
00-Governance/
技术成长/Java/
02-Spring-Ecosystem/
03-Database/
技术成长/数据与中间件/Redis/
技术成长/数据与中间件/消息队列/
06-Middleware/
07-Microservices/
08-JVM/
09-Concurrency/
10-Distributed-Systems/
11-Architecture/
12-Linux/
13-Docker/
14-Kubernetes/
15-DevOps/
16-Computer-Science/
17-Frontend/
技术成长/AI工程/
技术成长/C++嵌入式/
20-Project-Practice/
技术成长/00-通用/
技术成长/00-通用/
98-Personal-Topics/
99-Archive/
assets/
```

第三阶段迁移已有内容，优先顺序：

1. Java 集合、JVM、并发。
2. MySQL、Redis、消息队列、Elasticsearch。
3. Spring 生态、分布式、架构。
4. 计算机基础、AI 工程、C++。
5. 前端正式知识与 Vue Demo 归档。
6. 成长、面试、摄影和历史资料整理。

第四阶段开始批量生成缺失正式技术文档。所有新文档必须遵守 `Repository-Specification.md`。
