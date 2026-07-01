# 02 · Dockerfile 与镜像优化

> **目标读者**：写出生产级 Dockerfile，掌握多阶段构建、缓存、非 root、安全扫描。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. Dockerfile 指令速查

| 指令 | 作用 |
|------|------|
| `FROM` | 基础镜像，多阶段可多次 |
| `WORKDIR` | 工作目录 |
| `COPY` / `ADD` | 复制文件（优先 COPY） |
| `RUN` | 构建时执行，产生新层 |
| `ENV` | 环境变量 |
| `EXPOSE` | 文档声明端口，不自动 publish |
| `USER` | 运行用户 |
| `ENTRYPOINT` | 容器主命令 |
| `CMD` | 默认参数，可被 `docker run` 覆盖 |
| `ARG` | 构建参数，不进运行时 |
| `HEALTHCHECK` | 健康检查 |

---

## 2. ENTRYPOINT vs CMD

```dockerfile
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
CMD ["--spring.profiles.active=prod"]
```

```bash
docker run myapp --spring.profiles.active=dev
# 等价 java -jar app.jar --spring.profiles.active=dev
```

| 组合 | 行为 |
|------|------|
| 只有 CMD | 易被 run 参数整体替换 |
| ENTRYPOINT + CMD | run 参数追加到 ENTRYPOINT 后 |
| shell 形式 `CMD java -jar` | 会包一层 `/bin/sh -c`，信号处理差 |

**Java 推荐 exec 形式 JSON**：

```dockerfile
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 3. 多阶段构建（必会）

```dockerfile
# 阶段 1：编译
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /src
COPY pom.xml .
RUN mvn dependency:go-offline -B    # 仅 pom 变才重新拉依赖
COPY src ./src
RUN mvn package -DskipTests -B

# 阶段 2：运行
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=build /src/target/order-service.jar app.jar
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**收益**：最终镜像 **无 Maven、无源码**，从 ~800MB 降到 ~200MB。

### 3.1 依赖层缓存技巧

```dockerfile
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests
```

pom 不变则 **依赖下载层缓存命中**，CI 快很多。

---

## 4. 基础镜像选型

| 镜像 | 特点 |
|------|------|
| `eclipse-temurin:21-jre-alpine` | 小，musl libc，部分 JNI 需注意 |
| `eclipse-temurin:21-jre-jammy` | glibc，兼容性好，略大 |
| `distroless`（Google） | 无 shell，最安全，排障难 |

**Alpine + Java**：多数 Spring Boot 没问题；用到 **本地库 / 字体 / 某些 Agent** 时用 jammy。

---

## 5. 安全实践

```dockerfile
# 非 root
USER 1000

# 只读根文件系统（K8s securityContext 配合）
# docker run --read-only --tmpfs /tmp

# 不在镜像里写 SECRET
# 用 ENV 或 K8s Secret 挂载
```

| 禁忌 | 原因 |
|------|------|
| root 运行 | 容器逃逸后权限大 |
| latest 标签生产 | 不可追溯 |
| 把 keystore 密码写 Dockerfile | 泄露 |
| 超大 build context | 慢 + 可能打进敏感文件 |

```bash
docker scan myapp:1.0    # 漏洞扫描（Docker Scout / Trivy）
trivy image myapp:1.0
```

---

## 6. HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health/liveness || exit 1
```

| 参数 | 含义 |
|------|------|
| start-period | 启动宽限期，失败不计 retries |
| retries | 连续失败标记 unhealthy |

**K8s 用 probe 更细**；单机 Docker Compose 靠 HEALTHCHECK 做 `depends_on` 条件（Compose v2 `condition: service_healthy`）。

---

## 7. 构建参数与标签

```dockerfile
ARG JAR_FILE=target/app.jar
COPY ${JAR_FILE} app.jar

ARG BUILD_VERSION=unknown
LABEL org.opencontainers.image.version="${BUILD_VERSION}"
```

```bash
docker build --build-arg BUILD_VERSION=1.2.3 -t myapp:1.2.3 .
```

**Git commit 进镜像**（可追溯）：

```dockerfile
ARG GIT_SHA
LABEL git.sha=$GIT_SHA
```

---

## 8. 反模式

| 反模式 | 问题 |
|--------|------|
| 一个 RUN 装 20 个包又不清理 | 层膨胀 |
| `RUN apt update && apt install` 分两行 | 缓存失效 |
| 容器内 `mvn package` 无多阶段 | 镜像含 JDK+Maven |
| `COPY . .` 在第一行 | 任何文件改动 bust 全部缓存 |
| shell 形式 ENTRYPOINT | SIGTERM 到 sh 不到 Java |

**合并 RUN 并清理**：

```dockerfile
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

---

## 9. Jib 与 Buildpack（了解）

**Jib**（Maven）：

```xml
<plugin>
  <groupId>com.google.cloud.tools</groupId>
  <artifactId>jib-maven-plugin</artifactId>
</plugin>
```

```bash
mvn compile jib:build -Djib.to.image=registry/app:1.0
```

**Buildpacks**：

```bash
pack build myapp --builder paketobuildpacks/builder-jammy-base
```

面试：**Dockerfile 最通用**；Jib 适合纯 Java 无复杂 OS 依赖。

---

## 10. 自测

1. 写多阶段 Dockerfile 构建 Spring Boot fat jar。
2. 解释为何 `COPY pom.xml` 要在 `COPY src` 之前。
3. ENTRYPOINT exec 形式对优雅停机的影响？

---

→ 下一章：[03-网络存储与 Compose](./03-网络存储与Compose.md)

← [01-核心概念与架构](./01-核心概念与架构.md)
