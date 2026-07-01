# 05 · OpenFeign 与负载均衡

> **预计阅读**：50 min · **难度**：★★★★

---

## 1. OpenFeign 是什么

**声明式 HTTP 客户端**：写接口 + 注解，运行时动态代理发 HTTP。

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>
```

```java
@FeignClient(name = "pay-service", path = "/api/pay")
public interface PayClient {
    @GetMapping("/payments/{id}")
    PaymentDto getPayment(@PathVariable("id") Long id);

    @PostMapping("/payments")
    PaymentDto create(@RequestBody CreatePaymentRequest req);
}
```

```java
@SpringBootApplication
@EnableFeignClients
public class OrderApplication { }
```

---

## 2. 调用链

```
@FeignClient → JDK 动态代理
  → Contract 解析注解
  → LoadBalancer 选 pay-service 实例
  → HTTP Client（HttpURLConnection / OkHttp / HttpClient 5）
  → 解码 JSON
```

---

## 3. 超时与重试

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            connectTimeout: 3000
            readTimeout: 10000
          pay-service:
            readTimeout: 5000
```

**默认易超时**：Feign 读超时 60s 旧版不同，以当前 doc 为准。

**重试**：谨慎开启，非 GET 可能重复写。

```yaml
spring:
  cloud:
    loadbalancer:
      retry:
        enabled: false
```

---

## 4. 错误解码

```java
public class PayErrorDecoder implements ErrorDecoder {
    @Override
    public Exception decode(String methodKey, Response response) {
        if (response.status() == 404) {
            return new PaymentNotFoundException();
        }
        return new FeignException.errorStatus(methodKey, response);
    }
}
```

---

## 5. 传递 Header / Token

```java
@Configuration
public class FeignConfig {
    @Bean
    public RequestInterceptor authInterceptor() {
        return template -> {
            String token = TokenContext.get();
            if (token != null) {
                template.header("Authorization", "Bearer " + token);
            }
            String traceId = MDC.get("traceId");
            if (traceId != null) {
                template.header("X-Trace-Id", traceId);
            }
        };
    }
}
```

**注意**：RequestInterceptor 需注册到 **@FeignClient(configuration=...)** 且 **不要 @Component 全局污染**（除非有意）。

---

## 6. LoadBalancer

Ribbon 已移除，用 **Spring Cloud LoadBalancer**：

```java
@Bean
@LoadBalanced
public RestTemplate restTemplate() {
    return new RestTemplate();
}
```

自定义策略：

```java
@Bean
ReactorLoadBalancer<ServiceInstance> randomLoadBalancer(
        Environment env, LoadBalancerClientFactory factory) {
    // 自定义 ReactorServiceInstanceLoadBalancer
}
```

---

## 7. Feign vs RestTemplate vs WebClient vs gRPC

| | Feign | RestTemplate | WebClient | gRPC |
|---|-------|--------------|-----------|------|
| 风格 | 声明式 | 模板 | 响应式 | Protobuf |
| 适用 | 服务间 CRUD | 老代码 | 流式/非阻塞 | 高性能内部 |

---

## 8. 与 Sentinel 整合

```xml
<dependency>
  <groupId>com.alibaba.cloud</groupId>
  <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
```

Feign 集成 Sentinel 后，调用链受 **熔断规则** 保护；fallback：

```java
@FeignClient(name = "pay-service", fallbackFactory = PayClientFallbackFactory.class)
```

---

## 9. 坑

| 坑 | 处理 |
|----|------|
| GET 带 @RequestBody | 部分网关不支持；改 POST |
| 大对象 | 调大超时；或异步 MQ |
| 循环依赖 Feign | 架构问题，拆服务或事件驱动 |
| LocalDateTime 序列化 | 统一 Jackson 模块 |

---

→ [06-Sentinel 与 Seata](./06-Sentinel与Seata.md)

← [04-Spring Cloud Gateway](./04-SpringCloudGateway.md)
