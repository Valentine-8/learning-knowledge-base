# 03 · ELK 与 Loki 日志

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 日志可观测性目标

| 目标 | 说明 |
|------|------|
| 集中 | 多实例日志统一查询 |
| 检索 | 按 traceId、level、关键字秒级搜 |
| 关联 | 与 Metrics、Trace 联动 |
| 留存 | 合规与排障周期 |

---

## 2. ELK Stack

```
Apps（Logback JSON）
    │ Filebeat / Logstash
    ▼
Elasticsearch（存储 + 全文检索）
    │
    ▼
Kibana（查询 + 可视化）
```

| 组件 | 作用 |
|------|------|
| Elasticsearch | 分布式搜索引擎 |
| Logstash | ETL 管道，解析/transform |
| Kibana | UI、Dashboard |
| Filebeat | 轻量日志采集（推荐） |
| Beats | Metricbeat、Auditbeat 等 |

---

## 3. Java 日志格式

### JSON 结构化（推荐）

```xml
<!-- logback-spring.xml -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
  <encoder class="net.logstash.logback.encoder.LogstashEncoder">
    <includeMdcKeyName>traceId</includeMdcKeyName>
    <includeMdcKeyName>spanId</includeMdcKeyName>
  </encoder>
</appender>
```

输出：

```json
{
  "@timestamp": "2026-07-01T10:00:00.000Z",
  "level": "ERROR",
  "logger": "c.e.OrderService",
  "message": "Payment failed",
  "traceId": "abc123",
  "stack_trace": "..."
}
```

---

## 4. Filebeat 采集

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - /var/log/containers/*order-service*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["es:9200"]
  index: "order-service-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

K8s 常用 **DaemonSet** 部署 Filebeat 采集每个 Node 容器日志。

---

## 5. Kibana 查询（KQL）

```
level: "ERROR" and traceId: "abc123"
message: *NullPointerException*
@timestamp >= "2026-07-01T09:00:00"
```

| 功能 | 说明 |
|------|------|
| Discover | 原始日志浏览 |
| Dashboard | 错误趋势、Top 异常 |
| Index Pattern | 按天索引 order-service-* |
| ILM | 热温冷归档，自动删旧索引 |

---

## 6. Grafana Loki

**Loki** 只索引 **标签**（类似 Prometheus），日志内容压缩存储，成本低。

```
Promtail / Fluent Bit / Alloy
    │ push
    ▼
Loki
    │
    ▼
Grafana（Logs 面板，与 Metrics 同 UI）
```

### LogQL

```logql
{app="order-service"} |= "ERROR"
{namespace="prod"} | json | level="ERROR" | traceId="abc123"
rate({app="order-service"} |= "ERROR" [5m])
```

| 对比 ELK | Loki |
|----------|------|
| 全文索引 | 标签 + 过滤 |
| 功能强 | 轻量便宜 |
| 资源高 | K8s 友好 |
| 复杂查询 | LogQL |

---

## 7. 选型建议

| 场景 | 推荐 |
|------|------|
| 已有 ES 生态 | ELK |
| K8s + Grafana 全家桶 | Loki |
| 合规全文审计 | ELK |
| 成本敏感 | Loki + 对象存储 |

---

## 8. 日志最佳实践

| 实践 | 说明 |
|------|------|
| 结构化 | JSON，便于解析 |
| 级别规范 | ERROR=需行动，WARN=异常但恢复 |
| traceId | 每条日志带 traceId |
| 不打大对象 | 防 ES 膨胀 |
| 脱敏 | 手机、身份证、token |
| 采样 DEBUG | 生产默认 INFO |

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| ELK | 全文检索强，资源重 |
| Loki | 标签索引，Grafana 一体 |
| Filebeat | K8s 采集标配 |
| JSON | Java 日志标准化 |

---

← [02 链路追踪](./02-链路追踪SkyWalking-Jaeger.md) · [04 告警 SRE →](./04-告警与SRE.md)
