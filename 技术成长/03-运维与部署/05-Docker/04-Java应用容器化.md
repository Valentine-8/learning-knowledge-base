# 04 · Java 应用容器化

> **目标读者**：正确设置 JVM 堆与 cgroup、优雅停机、调试容器内 Java 进程，避免 OOM Kill。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. JVM 与容器内存（最高频坑）

### 1.1 问题

JDK 8u191 之前，JVM **看不到 cgroup memory limit**，按 **宿主机内存** 算默认堆 → 容器 limit 512M 但 JVM 堆 4G → **OOM Killed**。

### 1.2 现代 JDK（11+，推荐 17/21）

默认开启 **Container Support**：

```bash
java -XX:+PrintFlagsFinal -version | grep ActiveProcessorCount
java -XX:+PrintFlagsFinal -version | grep MaxHeapSize
```

**经验公式**（容器 memory limit = 1G）：

```
堆最大 ≈ limit × 70%～75%
留 native、元空间、线程栈、直接内存
```

```dockerfile
ENV JAVA_OPTS="-Xms512m -Xmx512m -XX:MaxMetaspaceSize=256m -XX:+UseG1GC"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

或显式百分比（JDK 10+）：

```bash
java -XX:MaxRAMPercentage=75.0 -XX:InitialRAMPercentage=75.0 -jar app.jar
```

| limit | 建议 -Xmx |
|-------|-----------|
| 512M | 256～384M |
| 1G | 512～768M |
| 2G | 1～1.5G |

### 1.3 监控 OOM Kill

```bash
docker inspect app --format='{{.State.OOMKilled}}'
dmesg | grep -i oom
```

K8s：`kubectl describe pod` → `Last State: Terminated, Reason: OOMKilled`

---

## 2. CPU 限制

```yaml
# Compose / K8s limits cpus: 1
```

JVM 默认 `-XX:ActiveProcessorCount` 识别 cgroup CPU quota，线程池大小会受影响。

**显式设置**（CPU 限制 2 核）：

```bash
-XX:ActiveProcessorCount=2
```

---

## 3. 优雅停机

Docker `docker stop` 发 **SIGTERM**，等待 **10s**（默认）后发 SIGKILL。

```yaml
# Spring Boot 2.3+
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 25s
```

```dockerfile
# 使用 tini 处理僵尸进程与信号转发
FROM eclipse-temurin:21-jre-alpine
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--", "java", "-jar", "app.jar"]
```

**K8s**：`terminationGracePeriodSeconds: 30` + `preStop` hook。

---

## 4. 时区与 locale

```dockerfile
ENV TZ=Asia/Shanghai
RUN apk add --no-cache tzdata && cp /usr/share/zoneinfo/$TZ /etc/localtime
```

日志时间与 cron、业务日期一致。

---

## 5. 字体与 headless

导出 PDF/验证码图片：

```dockerfile
RUN apk add --no-cache fontconfig ttf-dejavu
ENV JAVA_OPTS="-Djava.awt.headless=true"
```

---

## 6. 远程调试（仅开发）

```bash
docker run -e JAVA_TOOL_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005" \
  -p 8080:8080 -p 5005:5005 myapp
```

**生产禁止**开放 JDWP。

---

## 7. Arthas 进容器

```bash
docker exec -it app sh
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar
```

或 sidecar 模式（K8s 更常见）。

---

## 8. Spring Boot 3 + 原生镜像（了解）

GraalVM Native Image 启动快、内存小，但：

- 反射/动态代理需配置
- 构建慢
- 多数公司仍用 JRE 镜像

面试：知道即可，生产主流仍是 **Temurin JRE + fat jar**。

---

## 9. 完整生产 Dockerfile 模板

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /src
COPY pom.xml .
RUN mvn -B dependency:go-offline
COPY src ./src
RUN mvn -B package -DskipTests

FROM eclipse-temurin:21-jre-alpine
RUN apk add --no-cache tini tzdata wget \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
WORKDIR /app
RUN addgroup -S spring && adduser -S spring -G spring
COPY --from=build /src/target/*.jar app.jar
USER spring
ENV TZ=Asia/Shanghai \
    JAVA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+UseG1GC -Djava.security.egd=file:/dev/./urandom"
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s \
  CMD wget -qO- http://localhost:8080/actuator/health/liveness || exit 1
ENTRYPOINT ["/sbin/tini", "--", "sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| 容器 Java OOM Kill 原因？ | JVM 堆 > memory limit；或未识别 cgroup |
| MaxRAMPercentage 作用？ | 按容器可用内存比例算堆 |
| 为何要 tini？ | PID1 信号转发、回收僵尸进程 |
| 优雅停机怎么做？ | SIGTERM + Spring graceful + K8s preStop |

---

→ 下一章：[05-生产案例与面试题库](./05-生产案例与面试题库.md)

← [03-网络存储与 Compose](./03-网络存储与Compose.md)
