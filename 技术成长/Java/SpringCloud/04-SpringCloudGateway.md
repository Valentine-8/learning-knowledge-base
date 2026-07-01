# 04 · Spring Cloud Gateway

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. Gateway 是什么

基于 **Spring WebFlux + Netty** 的 **API 网关**：

- 路由（Path/Host/Header）
- 过滤器链（鉴权、限流、日志、改请求头）
- 与 Nacos 集成动态路由
- 非阻塞 IO

```
Client → Gateway (9090) → lb://order-service → 实例
```

---

## 2. 基本配置

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: order-route
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
          filters:
            - StripPrefix=2    # 去掉 /api/order
            - AddRequestHeader=X-Gateway, true
        - id: pay-route
          uri: lb://pay-service
          predicates:
            - Path=/api/pay/**
          filters:
            - StripPrefix=2
      default-filters:
        - name: Retry
          args:
            retries: 2
            statuses: BAD_GATEWAY
```

`lb://` = LoadBalancer + Nacos 实例。

---

## 3. Predicate 常用

| Predicate | 示例 |
|-----------|------|
| Path | `/api/**` |
| Host | `**.example.com` |
| Header | `X-Version, v2` |
| Method | GET |
| After/Before | 定时路由 |

**组合**：AND 关系。

---

## 4. Filter 类型

| 类型 | 示例 |
|------|------|
| 内置 GatewayFilter | StripPrefix, RewritePath, RequestRateLimiter |
| GlobalFilter | 全局鉴权、日志 |
| 自定义 GatewayFilterFactory | 业务逻辑 |

### 4.1 全局鉴权示例

```java
@Component
@Order(-1)
public class AuthGlobalFilter implements GlobalFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (!valid(token)) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        return chain.filter(exchange);
    }
}
```

---

## 5. 与 Sentinel 网关限流

```xml
<dependency>
  <groupId>com.alibaba.cloud</groupId>
  <artifactId>spring-cloud-alibaba-sentinel-gateway</artifactId>
</dependency>
```

Nacos 配 **gw-flow** 规则，按 routeId/API 分组限流。

---

## 6. 灰度路由

**元数据版本**：

```yaml
# 实例 metadata version=v2
spring:
  cloud:
    gateway:
      routes:
        - id: order-v2
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
            - Header=X-Version, v2
          metadata:
            version: v2
```

或自定义 **GrayLoadBalancer** 按 header 选实例。

---

## 7. Gateway vs Nginx

| 场景 | 选谁 |
|------|------|
| SSL、静态、极高 QPS | Nginx/Ingress |
| JWT 鉴权、与 Spring 生态 | Gateway |
| 混合 | Nginx → Gateway → 服务 |

见 [Nginx 专题](../../运维与部署/Nginx/README.md)。

---

## 8. 易错点

- **StripPrefix** 层数与 Controller `@RequestMapping` 对齐
- **CORS** 在 Gateway 统一配，避免重复
- **超时**：`spring.cloud.gateway.httpclient.connect-timeout/response-timeout`
- **RequestBody 只能读一次**：缓存 Body 用 `CachedBodyOutputMessage`

---

→ [05-OpenFeign 与负载均衡](./05-OpenFeign与负载均衡.md)

← [03-Nacos 配置中心](./03-Nacos配置中心.md)
