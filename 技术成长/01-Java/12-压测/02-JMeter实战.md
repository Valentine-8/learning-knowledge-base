# 02 · JMeter 实战

> **预计阅读**：90 min

---

## 1. JMeter 架构

```
Test Plan
├── Thread Group（虚拟用户）
│   ├── HTTP Request Sampler
│   ├── Header Manager
│   ├── CSV Data Set Config
│   └── Response Assertion
├── Listeners（报告）
└── Timers / Controllers
```

---

## 2. 快速上手

### 2.1 HTTP 接口压测

1. 添加 Thread Group：100 线程，Ramp-up 10s，循环 100 次
2. HTTP Request：方法、URL、Body
3. HTTP Header Manager：`Content-Type: application/json`
4. View Results Tree（调试）/ Summary Report（统计）

### 2.2 命令行（CI 推荐）

```bash
jmeter -n -t order.jmx -l result.jtl -e -o report/
```

- `-n` 非 GUI
- `-l` 结果文件
- `-e -o` 生成 HTML 报告

---

## 3. 参数化

```csv
# users.csv
userId,token
1001,eyJhbG...
1002,eyJhbG...
```

CSV Data Set Config：

- Filename: users.csv
- Variable Names: userId,token
- Recycle on EOF: true

HTTP Body：`{"userId": "${userId}"}`

---

## 4. 关联（动态 Token）

```
登录请求 → JSON Extractor 取 token → 后续请求 Header 引用 ${token}
```

PostProcessor：JSON Extractor / Regular Expression Extractor

---

## 5. 断言

| 组件 | 用途 |
|------|------|
| Response Assertion | 状态码、body 包含 |
| JSON Assertion | JSON Path |
| Duration Assertion | RT 上限 |

**压测统计应只计断言通过的请求**。

---

## 6. 定时器

| Timer | 作用 |
|-------|------|
| Constant Timer | 固定思考时间 |
| Gaussian Random Timer | 随机更真实 |
| Constant Throughput Timer | 控制 QPS 上限 |

---

## 7. 分布式压测

```
Master 协调 → 多台 Slave 执行 → 结果汇总
```

```bash
# Slave
jmeter-server

# Master
jmeter -n -t test.jmx -R slave1,slave2 -l result.jtl
```

**注意**：Slave 时钟同步；防火墙端口 1099/RMI。

---

## 8. 插件

| 插件 | 用途 |
|------|------|
| Custom Thread Groups | 阶梯加压 |
| PerfMon | 服务器资源监控 |
| JSON/YAML | 现代配置 |

Plugins Manager 安装。

---

## 9. 最佳实践

- **GUI 只写脚本**，压测用 CLI
- 禁用 View Results Tree（内存爆炸）
- 线程数不是越大越好（本机瓶颈）
- 分阶段加压：50 → 200 → 500 观察拐点
- 与 Grafana + InfluxDB 集成实时看板

---

## 10. 常见问题

| 问题 | 解决 |
|------|------|
| 连接被拒绝 | 本机端口耗尽，换分布式 |
| 结果不准 | 未参数化、缓存热点 |
| OOM | 减少 Listener、增大 heap |
| HTTPS 失败 | 导入证书或 HTTP Client4 |

---

## 11. 面试要点

1. JMeter 组件有哪些？
2. 如何实现参数化？
3. 分布式压测原理？
4. GUI 和 CLI 区别？
5. 如何关联登录 token？

← [01-压测理论](./01-压测理论与指标.md) · [03-Gatling](./03-Gatling与全链路压测.md)
