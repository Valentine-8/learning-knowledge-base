# 03 · Gatling 与全链路压测

> **预计阅读**：80 min

---

## 1. Gatling 特点

```
Scala DSL + 异步 IO + 精美 HTML 报告 + CI 友好
```

适合开发主导、版本管理的压测脚本。

---

## 2. 基础脚本

```scala
class OrderSimulation extends Simulation {
  val httpProtocol = http
    .baseUrl("https://api.example.com")
    .acceptHeader("application/json")

  val scn = scenario("Create Order")
    .exec(http("create")
      .post("/orders")
      .body(StringBody("""{"skuId":1,"qty":1}""")).asJson
      .check(status.is(201)))

  setUp(
    scn.inject(
      rampUsers(1000).during(60.seconds)
    )
  ).protocols(httpProtocol)
}
```

Maven 插件运行：

```bash
mvn gatling:test
```

报告在 `target/gatling/`。

---

## 3. 注入模型

```scala
// 阶梯
incrementUsersPerSec(10).times(10).eachLevelLasting(30.seconds)

// 恒定 QPS
constantUsersPerSec(100).during(5.minutes)

// 峰值浪涌
atOnceUsers(5000)
```

比 JMeter 更代码化、可复用。

---

## 4. Feeders（数据）

```scala
val feeder = csv("users.csv").random
scenario("Login").feed(feeder).exec(...)
```

JSON、JDBC、Redis feeder 支持动态数据。

---

## 5. Checks 与断言

```scala
.check(status.is(200))
.check(jsonPath("$.id").exists)
.check(responseTimeInMillis.lt(500))
```

失败请求单独统计。

---

## 6. Gatling vs JMeter

| 维度 | Gatling | JMeter |
|------|---------|--------|
| 脚本 | 代码 | GUI+XML |
| 资源占用 | 低（异步） | 较高 |
| 报告 | 内置优秀 | 需插件 |
| 非开发上手 | 难 | 易 |
| 录制 | 弱 | 强 |

---

## 7. 全链路压测

### 7.1 定义

从网关 → 微服务 → DB/MQ/cache **整条链路**加压，验证系统整体容量。

### 7.2 生产压测方式

| 方式 | 说明 |
|------|------|
| 隔离环境 | 预发 1:1，首选 |
| 影子流量 | 复制线上流量到 shadow 集群 |
| 流量染色 | 标记压测请求，走独立逻辑 |
| 小规模线上 | 极低比例 + 严格熔断 |

### 7.3 数据安全

- 压测数据打标，**禁止污染生产**
- 写操作走 Mock 或独立库
- 支付等调 sandbox

### 7.4 组织流程

```
方案评审 → 运维报备 → 监控值守 → 熔断预案 → 复盘
```

---

## 8. 与可观测性联动

- Gatling 输出 → InfluxDB → Grafana
- 链路 Trace：压测请求带 `X-Stress-Tag`
- 对齐 APM 火焰图定位热点

---

## 9. 最佳实践

- 脚本入 Git，Code Review
- 基准场景自动化 nightly
- 压测前 checklist：数据、监控、回滚
- 报告归档，版本对比

---

## 10. 面试要点

1. Gatling 和 JMeter 选型？
2. 全链路压测风险？
3. 影子流量原理？
4. 如何避免压测污染生产？
5. 压测报告如何解读？

← [02-JMeter](./02-JMeter实战.md) · [04-案例题库](./04-生产案例与面试题库.md)
