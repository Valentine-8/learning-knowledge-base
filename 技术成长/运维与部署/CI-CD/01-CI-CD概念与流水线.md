# 01 · CI/CD 概念与流水线

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 为什么需要 CI/CD

| 痛点 | CI/CD 解决 |
|------|-----------|
| 集成地狱 | 频繁合并，小步快跑 |
| 手工部署易错 | 自动化、可重复 |
| 反馈慢 | 提交即构建测试 |
| 回滚难 | 制品版本化 |

---

## 2. CI / CD 辨析

```
         CI                CD (Delivery)         CD (Deployment)
    ┌──────────┐         ┌──────────────┐       ┌──────────────┐
    │ 构建测试  │ ──────► │ 自动到预发   │ ────► │ 自动上生产   │
    │ 每次提交  │         │ 人工点发布   │       │ 全自动       │
    └──────────┘         └──────────────┘       └──────────────┘
```

多数企业 Java 团队处于 **Continuous Delivery**：预发自动，生产人工审批。

---

## 3. 流水线阶段设计

| 阶段 | 内容 | 时长目标 |
|------|------|----------|
| Checkout | 拉代码、子模块 | 秒级 |
| Build | mvn compile/package | 1～5 min |
| Unit Test | 单元测试 | 1～3 min |
| Static Analysis | Sonar、Checkstyle | 1～2 min |
| Integration Test | Testcontainers | 3～10 min |
| Package | jar/war | — |
| Docker Build | 镜像 | 1～5 min |
| Push Registry | Harbor/ECR | — |
| Deploy Dev/Staging | Helm/K8s | 1～3 min |
| E2E / Smoke | 冒烟测试 | 2～5 min |
| Deploy Prod | 蓝绿/金丝雀 | 视策略 |

**原则**：失败快速（fail fast），慢测试后置或并行。

---

## 4. 分支策略

| 策略 | 说明 |
|------|------|
| Git Flow | develop/release/hotfix，较重 |
| GitHub Flow | main + feature PR，轻量 |
| GitLab Flow | environment 分支 |
| Trunk Based | 主干开发，feature flag |

Java 微服务常见：**main 保护 + PR + 自动 CI**。

---

## 5. 发布策略

### 滚动发布（Rolling）

逐批替换 Pod，K8s 默认。简单，但新旧共存。

### 蓝绿发布（Blue-Green）

两套环境，流量一键切换。资源双倍，回滚快。

### 金丝雀（Canary）

5% → 20% → 100% 逐步放量，观察指标。需 Ingress/Service Mesh。

### 灰度 + Feature Flag

代码已上生产，功能开关控制。Unleash、LaunchDarkly。

---

## 6. 环境管理

| 环境 | 用途 |
|------|------|
| local | 开发 |
| dev | 联调 |
| test/QA | 测试 |
| staging | 生产镜像预演 |
| prod | 生产 |

**配置分离**：Spring Profile + 配置中心（Nacos），密钥用 Vault/云 KMS。

---

## 7. Pipeline as Code

流水线定义放 Git，可 Review、版本化：

- Jenkinsfile（Groovy）
- `.gitlab-ci.yml`
- `.github/workflows/*.yml`

好处：变更可追溯，与代码同生命周期。

---

## 8. DORA 指标（了解）

| 指标 | 精英团队参考 |
|------|-------------|
| 部署频率 | 按需多次/天 |
| 变更前置时间 | < 1 天 |
| 变更失败率 | < 15% |
| 恢复时间 MTTR | < 1 小时 |

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| CI | 每次提交自动构建测试 |
| CD | 交付=可发布；部署=自动上生产 |
| 发布 | 滚动简单，金丝雀安全 |
| Pipeline as Code | 流水线即代码 |

---

← [00 速查](./00-速查总览.md) · [02 Jenkins GitLab →](./02-Jenkins与GitLab-CI.md)
