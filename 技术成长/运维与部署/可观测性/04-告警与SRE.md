# 04 · 告警与 SRE

> **预计阅读**：50 min · **难度**：★★★★

---

## 1. SRE 核心理念

**SRE**（Site Reliability Engineering）用软件工程方法运维：

| 原则 | 说明 |
|------|------|
| SLO 驱动 | 用目标衡量可靠性 |
| 错误预算 | 允许一定失败空间 |
| Toil 减少 | 自动化重复劳动 |
| 事后复盘 | Blameless Postmortem |

---

## 2. SLI / SLO / SLA

| 术语 | 含义 | 示例 |
|------|------|------|
| SLI | 服务水平指标 | 成功请求比例 |
| SLO | 目标值 | 99.9% 可用 |
| SLA | 合同 | 未达标赔偿 |

**可用性计算**：

```
99.9%（三个九）= 每月约 43 分钟不可用
99.99%（四个九）= 每月约 4.3 分钟
```

**SLI 示例 — 订单 API**：

```promql
# 可用性 SLI：非 5xx 比例
sum(rate(http_server_requests_seconds_count{uri="/api/orders",status!~"5.."}[30d]))
/ sum(rate(http_server_requests_seconds_count{uri="/api/orders"}[30d]))
```

---

## 3. 错误预算

```
错误预算 = 1 - SLO
99.9% SLO → 0.1% 错误预算

预算耗尽 → 停止发版，专注稳定性
预算充足 → 可激进发布新功能
```

平衡 **创新速度** 与 **可靠性** 的量化工具。

---

## 4. 告警设计

### 好告警

- 有明确 **runbook**（处理手册）
- 用户可感知的问题
- 需要人介入

### 坏告警

- 磁盘 80%（还有空间）
- 每次 deploy 都告警
- 无法行动的通知

### 告警分级

| 级别 | 响应 | 示例 |
|------|------|------|
| P0 | 5 分钟，电话 | 核心 API 全挂 |
| P1 | 15 分钟 | 错误率 > 5% |
| P2 | 工作时间 | 单 Pod 重启 |
| P3 | 工单 | 证书 30 天过期 |

---

## 5. On-Call 与 Runbook

**Runbook 模板**：

```markdown
## 告警：HighErrorRate order-service

### 影响
用户下单失败

### 排查
1. Grafana 看 QPS 和错误分布
2. Kibana traceId 查 ERROR 堆栈
3. 最近 deploy？kubectl rollout history
4. 依赖服务 payment 健康？

### 缓解
- 回滚：kubectl rollout undo
- 扩容：kubectl scale

### 升级
15 分钟未恢复 → 呼叫 SRE Lead
```

---

## 6. 黄金信号 + RED/USE

### 服务（RED）

- **R**ate：请求速率
- **E**rrors：错误率
- **D**uration：延迟

### 资源（USE）

- **U**tilization：CPU、磁盘
- **S**aturation：队列、连接池满
- **E**rrors：硬件错误

---

## 7. Incident 管理

```
检测 → 响应 → 缓解 → 修复 → 复盘
```

| 实践 | 说明 |
|------|------|
| 指挥官 | 一人协调，避免混乱 |
| 沟通频道 | 专用 war room |
| 时间线 | 记录每步操作 |
| Postmortem | 5 Whys，改系统非改人 |

---

## 8. 容量规划

| 方法 | 说明 |
|------|------|
| 压测 | JMeter/Gatling 找上限 |
| 趋势 | Prometheus 预测 30 天 |
| 头room | 峰值 70% 饱和度告警 |
| HPA | K8s 自动扩缩 |

---

## 9. 可观测性成熟度

| 级别 | 特征 |
|------|------|
| L0 | 只有日志文件 SSH 看 |
| L1 | 集中日志 + 基础监控 |
| L2 | Metrics + Trace + 告警 |
| L3 | SLO 驱动 + 错误预算 |
| L4 | 自动 remediation、混沌工程 |

---

## 10. 小结

| 要点 | 一句话 |
|------|--------|
| SLO | 量化可靠性目标 |
| 错误预算 | 平衡发版与稳定 |
| 告警 | 少而 actionable |
| Runbook | 告警必须配处理手册 |

---

← [03 ELK Loki](./03-ELK与Loki日志.md) · [05 生产案例 →](./05-生产案例与面试题库.md)
