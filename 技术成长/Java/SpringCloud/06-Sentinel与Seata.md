# 06 · Sentinel 与 Seata

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. Sentinel 是什么

阿里开源 **流量治理**：限流、熔断、降级、系统保护、热点参数。

```
调用进入 → Slot 链（统计、规则检查）→ 通过 / 阻塞 / 降级
```

**对比 Hystrix**：Sentinel 更细规则、控制台、国内文档好；Hystrix 停更。

---

## 2. 接入

```yaml
spring:
  cloud:
    sentinel:
      transport:
        dashboard: localhost:8080
      eager: true
```

依赖：`spring-cloud-starter-alibaba-sentinel`

---

## 3. 流控规则

| 维度 | 说明 |
|------|------|
| QPS | 每秒请求数 |
| 并发线程数 | 同时执行数 |
| 关联流控 | 关联资源限流 |
| 链路入口 | 只限从某入口来的调用 |

```java
@SentinelResource(value = "createOrder", blockHandler = "createBlock")
public Order createOrder(CreateOrderCmd cmd) { ... }

public Order createBlock(CreateOrderCmd cmd, BlockException ex) {
    throw new BizException("系统繁忙，请稍后");
}
```

**热点参数**：商品 ID 级别限流。

---

## 4. 熔断规则

| 策略 | 说明 |
|------|------|
| 慢调用比例 | RT 超阈值比例达线熔断 |
| 异常比例 | 异常占比 |
| 异常数 | 窗口内异常次数 |

状态机：**closed → open → half-open**（试探恢复）。

Feign + Sentinel：自动对 `@FeignClient` 资源名生效（需在 dashboard 配规则）。

---

## 5. 与 Nginx / Gateway 分工

| 层 | 工具 | 作用 |
|----|------|------|
| 入口 | Nginx limit_req | IP、防刷 |
| 网关 | Sentinel gw-flow | 按 API 路由 |
| 服务 | Sentinel @SentinelResource | 细粒度、热点 |
| 依赖 | Feign 熔断 | 下游挂保护自身 |

---

## 6. Seata 分布式事务

**问题**：订单服务扣库存 + 支付服务扣款，跨库需一致。

### 6.1 AT 模式（常用，无侵入）

```
TM 开启全局事务
  → RM1 订单库：执行业务 SQL + 存 undo_log
  → RM2 支付库：同上
  → TC 协调：全提交删 undo；任失败回滚用 undo 补偿
```

```java
@GlobalTransactional(name = "create-order-tx", rollbackFor = Exception.class)
public void createOrder(OrderCmd cmd) {
    orderService.create(cmd);
    payClient.deduct(cmd.getPayRequest());  // Feign
}
```

### 6.2 前提

- 每服务 **独立数据库**
-  undo_log 表
- Seata Server（TC）部署

### 6.3 TCC / Saga

| 模式 | 说明 |
|------|------|
| TCC | Try-Confirm-Cancel，手写三接口 |
| Saga | 长事务，正向 + 补偿，最终一致 |

**7 年建议**：能说 AT 原理；生产很多用 **本地消息表 + MQ** 替代强分布式事务。

---

## 7. 选型建议

| 场景 | 方案 |
|------|------|
| 读多写少峰值 | Sentinel 限流 |
| 下游不稳定 | Feign 熔断 + 降级数据 |
| 强一致跨库 | Seata AT（评估性能）或 TCC |
| 可最终一致 | 本地消息表 / Outbox |

---

→ [07-生产案例与面试题库](./07-生产案例与面试题库.md)

← [05-OpenFeign 与负载均衡](./05-OpenFeign与负载均衡.md)
