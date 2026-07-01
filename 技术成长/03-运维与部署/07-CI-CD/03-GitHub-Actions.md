# 03 · GitHub Actions

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 架构

```
GitHub Repository
  └── .github/workflows/*.yml
        │
        ▼
GitHub-hosted Runner / Self-hosted Runner
  └── Job → Steps（actions + run）
```

| 概念 | 说明 |
|------|------|
| Workflow | 自动化流程，YAML 定义 |
| Event | push、PR、schedule、workflow_dispatch |
| Job | 并行或串行任务单元 |
| Step | 单步：action 或 shell |
| Action | 可复用单元（Marketplace） |

---

## 2. 完整 Java CI 示例

```yaml
name: Java CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven

      - name: Build and Test
        run: mvn -B verify

      - name: Upload Test Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: target/surefire-reports/

  docker:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

---

## 3. 常用特性

### 矩阵构建

```yaml
strategy:
  matrix:
    java: [11, 17, 21]
steps:
  - uses: actions/setup-java@v4
    with:
      java-version: ${{ matrix.java }}
```

### 密钥

```yaml
env:
  DB_PASS: ${{ secrets.DB_PASSWORD }}
```

Settings → Secrets and variables → Actions 配置。

### 手动触发

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target env'
        required: true
        default: 'staging'
```

### 复用 Workflow

```yaml
jobs:
  call-reusable:
    uses: org/repo/.github/workflows/reusable-ci.yml@v1
    secrets: inherit
```

---

## 4. 热门 Actions

| Action | 用途 |
|--------|------|
| actions/checkout | 拉代码 |
| actions/setup-java | JDK + Maven/Gradle 缓存 |
| actions/cache | 通用缓存 |
| docker/build-push-action | 构建推送镜像 |
| actions/upload-artifact | 产物上传 |
| codecov/codecov-action | 覆盖率上报 |
| snyk/actions | 安全扫描 |

---

## 5. Self-hosted Runner

适合访问内网 Harbor、部署私有 K8s：

```bash
# 在内网机器注册
./config.sh --url https://github.com/org/repo --token TOKEN
./run.sh
```

```yaml
jobs:
  deploy:
    runs-on: self-hosted
    steps:
      - run: kubectl apply -f k8s/
```

---

## 6. 与 Jenkins/GitLab 选型

| 场景 | 推荐 |
|------|------|
| 开源项目 GitHub | Actions 零配置 |
| 企业内网 GitLab | GitLab CI |
| 复杂多系统编排 | Jenkins |
| 混合 | Actions CI + Argo CD 部署 |

---

## 7. 小结

| 要点 | 一句话 |
|------|--------|
| Workflow | event 触发 job 跑 steps |
| Marketplace | 复用 actions 加速搭建 |
| secrets | 敏感信息放 Secrets |
| cache | setup-java 自带 Maven 缓存 |

---

← [02 Jenkins GitLab](./02-Jenkins与GitLab-CI.md) · [04 质量门禁 →](./04-质量门禁与制品.md)
