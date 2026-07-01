# 01 · Prometheus 与 Grafana

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. Prometheus 架构

```
Exporters / Apps（/metrics）
    │ pull（HTTP scrape）
    ▼
Prometheus Server
  ├── TSDB（时序存储）
  ├── PromQL 引擎
  └── Alertmanager ──► 邮件/钉钉/PagerDuty
            │
            ▼
        Grafana（可视化）
```

| 特点 | 说明 |
|------|------|
| Pull 模型 | Prometheus 主动拉取 |
| 多维标签 | `{method="GET", status="200"}` |
| PromQL | 查询语言 |
| 无集群依赖 | 单机起步，联邦/Thanos 扩展 |

---

## 2. 指标类型

| 类型 | 用途 | 示例 |
|------|------|------|
| Counter | 只增计数 | 请求总数、错误数 |
| Gauge | 可增可减 | 内存、队列长度 |
| Histogram | 分桶分布 | 延迟分布 |
| Summary | 分位数（客户端算） | 较少用，推荐 Histogram |

Spring Boot Micrometer 自动暴露：

```
http_server_requests_seconds_count
http_server_requests_seconds_sum
http_server_requests_seconds_bucket{le="0.1"}
jvm_memory_used_bytes
hikaricp_connections_active
```

---

## 3. scrape 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'order-service'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['order-svc:8080']
        labels:
          env: prod

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

K8s 环境用 **ServiceMonitor**（Prometheus Operator）自动发现。

---

## 4. PromQL 实战

```promql
# 5 分钟 QPS
sum(rate(http_server_requests_seconds_count{application="order-service"}[5m]))

# 按 status 分组错误率
sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m]))
/ sum(rate(http_server_requests_seconds_count[5m]))

# P99 延迟（秒）
histogram_quantile(0.99,
  sum by (le) (rate(http_server_requests_seconds_bucket[5m])))

# 连接池使用率
hikaricp_connections_active / hikaricp_connections_max

# 预测磁盘（线性）
predict_linear(node_filesystem_avail_bytes[1h], 4*3600)
```

| 函数 | 用途 |
|------|------|
| rate | Counter 每秒增速 |
| increase | 时间段增量 |
| histogram_quantile | 分位数 |
| sum by | 聚合 |
| avg_over_time | 滑动平均 |

---

## 5. 告警规则

```yaml
# rules.yml
groups:
  - name: order-service
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_server_requests_seconds_count{application="order-service",status=~"5.."}[5m]))
          / sum(rate(http_server_requests_seconds_count{application="order-service"}[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "错误率超过 5%"

      - alert: HighP99Latency
        expr: |
          histogram_quantile(0.99, sum(rate(http_server_requests_seconds_bucket{application="order-service"}[5m])) by (le)) > 2
        for: 10m
        labels:
          severity: warning
```

---

## 6. Alertmanager

```yaml
route:
  receiver: 'default'
  group_by: ['alertname', 'application']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pager'

receivers:
  - name: 'pager'
    webhook_configs:
      - url: 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
```

---

## 7. Grafana

### 数据源

添加 Prometheus → 写 PromQL → 选可视化（Graph、Stat、Gauge、Table）。

### 常用大盘面板

| 面板 | PromQL 思路 |
|------|-------------|
| QPS | rate(count) |
| 延迟 | histogram_quantile |
| 错误率 | 5xx / total |
| JVM 堆 | jvm_memory_* |
| GC | jvm_gc_pause_seconds |
| Pod CPU | container_cpu_usage_seconds |

### 变量

```
$application = label_values(http_server_requests_seconds_count, application)
```

Dashboard as Code：Jsonnet / Grafana Provisioning。

---

## 8. Java 自定义指标

```java
@Service
public class OrderMetrics {
  private final Counter orderCreated;
  private final Timer paymentLatency;

  public OrderMetrics(MeterRegistry registry) {
    this.orderCreated = Counter.builder("order.created")
        .tag("channel", "web")
        .register(registry);
    this.paymentLatency = Timer.builder("payment.latency")
        .publishPercentiles(0.5, 0.99)
        .register(registry);
  }

  public void onOrderCreated() { orderCreated.increment(); }
}
```

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| Pull | Prometheus scrape /actuator/prometheus |
| Histogram | 算 P99 用 bucket + histogram_quantile |
| 告警 | for 持续时间防抖动 |
| Grafana | 黄金信号大盘必备 |

---

← [00 速查](./00-速查总览.md) · [02 链路追踪 →](./02-链路追踪SkyWalking-Jaeger.md)
