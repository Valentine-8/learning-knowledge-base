# 02 · 链路追踪 SkyWalking / Jaeger

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 为什么需要链路追踪

微服务一次请求经过网关 → 订单 → 库存 → 支付，日志分散，难以定位慢点。

**分布式追踪**用 **TraceId** 串联各服务 **Span**，还原调用链路与耗时。

```
Trace (traceId: abc123)
  ├── Span: Gateway GET /api/order     50ms
  │     └── Span: OrderService.create  45ms
  │           ├── Span: DB insert      10ms
  │           └── Span: Inventory RPC    30ms  ← 瓶颈
  └── ...
```

---

## 2. 核心概念

| 概念 | 说明 |
|------|------|
| Trace | 一次完整请求 |
| Span | 一个操作单元（HTTP、SQL、MQ） |
| traceId | 全局唯一，跨服务传递 |
| spanId | Span 唯一 ID |
| parentSpanId | 父 Span |
| Tags | 键值元数据 |
| Logs | Span 内事件 |

**透传 Header**（W3C Trace Context）：

```
traceparent: 00-{traceId}-{spanId}-01
```

---

## 3. SkyWalking

Apache 开源 APM，Java 生态友好，**字节码 Agent** 无侵入。

### 架构

```
Java App + skywalking-agent.jar
    │ gRPC
    ▼
SkyWalking OAP（收集、分析、存储）
    │
    ▼
SkyWalking UI / Grafana
Storage: Elasticsearch / H2 / BanyanDB
```

### Java 启动

```bash
java -javaagent:/path/skywalking-agent.jar \
  -DSW_AGENT_NAME=order-service \
  -DSW_AGENT_COLLECTOR_BACKEND_SERVICES=oap:11800 \
  -jar order-service.jar
```

K8s 用 initContainer 挂载 agent。

### 能力

| 功能 | 说明 |
|------|------|
| 拓扑图 | 服务依赖自动发现 |
| 慢 SQL | JDBC 拦截 |
| 异常分析 | 堆栈聚合 |
| 告警 | OAP 规则 |
| 日志关联 | traceId 写 MDC |

---

## 4. Jaeger / Zipkin

CNCF Jaeger，兼容 OpenTracing / OpenTelemetry。

```
App（OpenTelemetry SDK / Agent）
    │ UDP/HTTP
    ▼
Jaeger Collector
    ▼
Storage（Elasticsearch / Cassandra）
    ▼
Jaeger UI
```

### Spring Boot 3 + Micrometer Tracing

```xml
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```

```yaml
management:
  tracing:
    sampling:
      probability: 0.1   # 10% 采样
  otlp:
    tracing:
      endpoint: http://jaeger:4318/v1/traces
```

---

## 5. SkyWalking vs Jaeger

| 维度 | SkyWalking | Jaeger |
|------|------------|--------|
| 侵入性 | Agent 无侵入 | OTel SDK/Agent |
| Java 支持 | 极强 | 好 |
| 存储 | ES 等 | ES/Cassandra |
| 生态 | 国内常用 | K8s/CNCF 标准 |
| 趋势 | 持续维护 | OpenTelemetry 统一 |

**建议**：新项目跟 **OpenTelemetry**；国内存量 SkyWalking 多。

---

## 6. 采样策略

| 策略 | 说明 |
|------|------|
| 固定比例 | 10% 采样，降存储 |
| 速率限制 | 每秒最多 N 条 |
| 错误优先 | 错误全采，正常采样 |
| 自适应 | 高负载降采样 |

生产高 QPS 必须采样，否则存储和性能扛不住。

---

## 7. 跨线程与 MQ

| 场景 | 处理 |
|------|------|
| @Async | Agent 自动传播（SkyWalking） |
| 线程池 | 手动包装 Runnable 或 TTL |
| Kafka | 消费端从 Header 取 traceId |
| Feign | 自动注入 Header |

```java
// 手动传播示例（OTel）
Span parent = tracer.currentSpan();
try (Tracer.SpanInScope ws = tracer.withSpan(parent)) {
  executor.submit(() -> {
    try (Tracer.SpanInScope ws2 = tracer.withSpan(parent)) {
      doWork();
    }
  });
}
```

---

## 8. 排障实战

1. 用户反馈下单慢 → Grafana P99 升高
2. SkyWalking 按 traceId 或 endpoint 查 Trace
3. 发现 Inventory RPC 30ms，展开看 SQL 10ms + Redis 20ms
4. Redis 慢日志 → 大 key 问题
5. 修复 + 验证 Trace 耗时下降

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| Trace/Span | traceId 串全链路 |
| SkyWalking | Java Agent 零代码 |
| OTel | 行业标准方向 |
| 采样 | 高 QPS 必配 |

---

← [01 Prometheus](./01-Prometheus与Grafana.md) · [03 ELK Loki →](./03-ELK与Loki日志.md)
