# 03 · WebFlux 与 MVC 选型

> **预计阅读**：80 min

---

## 1. 架构对比

| 维度 | Spring MVC | Spring WebFlux |
|------|------------|----------------|
| 服务器 | Tomcat/Jetty | Netty（默认） |
| 模型 | 每请求一线程（阻塞） | 事件循环（非阻塞） |
| 编程 | 命令式 | 响应式（Mono/Flux） |
| JDBC | 原生支持 | 需 R2DBC 或包装 |
| 生态 | 最成熟 | 较小 |
| 学习成本 | 低 | 高 |

---

## 2. 何时选 WebFlux

| 场景 | 理由 |
|------|------|
| Spring Cloud Gateway | 官方基于 WebFlux |
| 高并发长连接 | WebSocket、SSE 大量连接 |
| 全链路 reactive | R2DBC + Reactive Redis + WebClient |
| IO 聚合 | 并行调多个下游，延迟敏感 |

---

## 3. 何时选 MVC（多数业务）

| 场景 | 理由 |
|------|------|
| CRUD 为主 | 简单直接 |
| MyBatis/JDBC | 生态成熟 |
| 团队经验 | 阻塞模型更好维护 |
| Java 21 虚拟线程 | 阻塞 IO 成本大降 |

```java
// Spring Boot 3.2+ 虚拟线程
spring.threads.virtual.enabled=true
```

**趋势**：虚拟线程出现后，「为 IO 上 WebFlux」的动机减弱，但 Gateway 等场景仍需要。

---

## 4. 性能误区

```
WebFlux ≠ 总是更快
```

- CPU 密集：两者差不多，都要多核并行
- 阻塞栈 + 小线程池：并发能力差
- WebFlux + 阻塞 JDBC：假 reactive，还需 boundedElastic
- 正确压测才有结论

---

## 5. 混合架构

常见现实方案：

```
Gateway (WebFlux) → 后端 MVC 微服务 (阻塞 JDBC)
```

或 MVC 服务内用 WebClient 非阻塞调下游（注意线程切换）。

---

## 6. Spring Cloud Gateway

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: order
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
```

- 基于 WebFlux + Netty
- 过滤器链：限流、鉴权、重写
- 对比 Nginx：Java 生态集成好，资源占用更高

---

## 7. 迁移评估清单

- [ ] 是否有全链路 reactive 收益？
- [ ] 团队 Reactor 熟练度？
- [ ] 数据层能否 R2DBC？
- [ ] 第三方 SDK 是否阻塞？
- [ ] 虚拟线程能否满足需求？

**建议**：新项目默认 MVC + 虚拟线程；明确 Gateway/高连接场景用 WebFlux。

---

## 8. 决策 ADR 示例

```markdown
## 决策：订单服务保持 MVC + 虚拟线程
- 理由：MyBatis 为主，团队无 Reactor 经验
- 网关层已用 Gateway 扛入口并发
- 压测虚拟线程下 P99 满足 SLA
```

---

## 9. 面试要点

1. WebFlux 和 MVC 核心区别？
2. WebFlux 一定更快吗？
3. 虚拟线程对选型影响？
4. Gateway 为什么用 WebFlux？
5. 阻塞 JDBC 在 WebFlux 项目怎么办？

← [02-WebFlux核心](./02-SpringWebFlux核心.md) · [04-案例题库](./04-生产案例与面试题库.md)
