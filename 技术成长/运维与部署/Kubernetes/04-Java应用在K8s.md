# 04 · Java 应用在 Kubernetes

> **目标读者**：为 Spring Boot 配置资源、探针、JVM、ConfigMap/Secret、HPA 与优雅停机。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 完整 Deployment 模板

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-app
  namespace: prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-app
  template:
    metadata:
      labels:
        app: order-app
    spec:
      terminationGracePeriodSeconds: 45
      containers:
        - name: app
          image: harbor.example.com/order/app:1.2.3
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: prod
            - name: JAVA_OPTS
              value: "-XX:MaxRAMPercentage=75.0 -XX:+UseG1GC"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          startupProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            failureThreshold: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            periodSeconds: 10
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["sh", "-c", "sleep 10"]
      imagePullSecrets:
        - name: harbor-secret
```

---

## 2. 资源 requests / limits

| | requests | limits |
|---|----------|--------|
| 作用 | 调度依据（保证资源） | 运行时上限 |
| CPU | 可压缩，超用 throttle | 硬上限 |
| Memory | 调度 | 超限 → OOM Kill |

**Java 配对**：

```
limits.memory = 1Gi  →  MaxRAMPercentage=75  →  堆 ~768Mi
requests.memory 略低于 limits，便于调度
```

```bash
kubectl top pod -n prod
kubectl describe node | grep -A5 Allocated
```

---

## 3. Spring Boot Actuator 探针

`application-prod.yml`：

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
```

| 探针 | 应检查 | 不应检查 |
|------|--------|----------|
| liveness | JVM 活着、死锁 | 外部 DB 挂（会误杀） |
| readiness | 应用可接流量、依赖就绪 | — |

**自定义 readiness**（DB 可选）：

```java
@Component
public class DbReadinessIndicator implements HealthIndicator {
    @Override
    public Health health() {
        // 检测 DB，失败 return Health.down()
    }
}
```

---

## 4. 优雅停机全链路

```
1. kubectl delete pod / 滚动更新
2. Pod 标记 Terminating
3. Endpoints 移除（readiness 失败）→ 无新流量
4. preStop sleep（等 SLB/Ingress 传播）
5. SIGTERM → Spring graceful shutdown
6. terminationGracePeriodSeconds 内完成
7. SIGKILL
```

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sh", "-c", "sleep 15"]
terminationGracePeriodSeconds: 45
```

```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

---

## 5. ConfigMap 外置配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-app-config
data:
  application-prod.yaml: |
    spring:
      datasource:
        url: jdbc:mysql://mysql.prod:3306/order
```

挂载：

```yaml
args:
  - --spring.config.additional-location=file:/config/
volumeMounts:
  - name: config
    mountPath: /config
    readOnly: true
```

或使用 **Spring Cloud Kubernetes** 动态刷新。

---

## 6. HPA 与 Java

CPU 对 Java 不总是灵敏（GC 尖刺）；可结合：

- **自定义指标**：Prometheus Adapter → QPS、线程池队列
- **KEDA**：按 MQ 堆积伸缩

```yaml
metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

---

## 7. Init Container

```yaml
initContainers:
  - name: wait-mysql
    image: busybox:1.36
    command: ['sh', '-c', 'until nc -z mysql 3306; do sleep 2; done']
```

等依赖就绪再启 Java（也可用 readiness 更精细）。

---

## 8. 调试与 Arthas

```bash
kubectl port-forward pod/order-app-xxx 8080:8080
kubectl exec -it order-app-xxx -- jcmd 1 VM.flags
```

**Ephemeral debug 容器**（K8s 1.23+）：

```bash
kubectl debug -it order-app-xxx --image=busybox --target=app
```

---

## 9. 多环境

| 方式 | 说明 |
|------|------|
| namespace | prod / staging |
| Kustomize overlay | 同 base 不同 patch |
| Helm values | chart + values-prod.yaml |

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| Java 容器如何设堆？ | MaxRAMPercentage，limit 的 70～75% |
| 三类探针区别？ | startup/readiness/liveness |
| preStop 为何 sleep？ | 等 Ingress/Endpoints 摘流量 |
| requests 不设会怎样？ | BestEffort QoS，易被驱逐 |

---

→ 下一章：[05-排障运维与面试题库](./05-排障运维与面试题库.md)

← [03-网络存储与 Ingress](./03-网络存储与Ingress.md)
