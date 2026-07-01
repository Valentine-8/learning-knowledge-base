# 02 · Nacos 注册发现

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 服务注册

```xml
<dependency>
  <groupId>com.alibaba.cloud</groupId>
  <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
```

```yaml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: prod
        group: DEFAULT_GROUP
        metadata:
          version: v1
          zone: cn-hangzhou-a
```

启动后 Nacos 控制台可见实例：**IP:Port、健康状态、元数据**。

---

## 2. 服务发现与 LoadBalancer

```java
@LoadBalanced
@Bean
public RestTemplate restTemplate() {
    return new RestTemplate();
}

// 调用
restTemplate.getForObject("http://order-service/orders/1", Order.class);
```

`order-service` 解析为 Nacos 实例列表 + 负载均衡（默认 RoundRobin）。

**Feign** 内部同样用 `DiscoveryClient` + LoadBalancer。

---

## 3. 健康检查

| 方式 | 说明 |
|------|------|
| 客户端心跳 | 默认，服务向 Nacos 续约 |
| 服务端探测 | 注册临时实例 + 主动 HTTP/TCP 检查 |

Spring Boot Actuator：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health
```

Nacos 2.x 支持 **gRPC 长连接** 推送实例变更，减少轮询。

---

## 4. 命名空间与分组

```
Namespace: prod / staging / dev     ← 环境隔离
Group: DEFAULT_GROUP / ORDER_GROUP    ← 逻辑分组
Service: order-service                ← 服务名
Cluster: DEFAULT / hangzhou           ← 机房/单元
```

**多环境**：不同 namespace，避免 test 实例被 prod 消费。

---

## 5. 权重与下线

```bash
# Nacos API 或控制台
权重 0 = 不下流量（平滑下线）
```

发布流程：

1. 权重调 0 或 readiness fail
2. 等待流量 drain
3. 停进程

---

## 6. 同 zone 优先

```yaml
spring:
  cloud:
    loadbalancer:
      configurations: zone-preference
    nacos:
      discovery:
        metadata:
          zone: zone-a
```

减少跨机房调用 RT。

---

## 7. AP / CP 模式

| 模式 | 场景 |
|------|------|
| AP | 注册发现默认，可用性优先 |
| CP | 强一致配置（Raft），如 Nacos 2.x 部分能力 |

**面试**：Eureka AP；Nacos 可切换；CP 适合配置不丢。

---

## 8. 与 K8s

K8s 自带 Service DNS；仍用 Nacos 场景：

- 混合部署（VM + K8s）
- 统一注册、多数据中心
- 元数据路由（version、gray）

---

→ [03-Nacos 配置中心](./03-Nacos配置中心.md)

← [01-微服务组件全景](./01-微服务组件全景.md)
