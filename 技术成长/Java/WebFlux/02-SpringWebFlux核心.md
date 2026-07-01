# 02 · Spring WebFlux 核心

> **预计阅读**：90 min

---

## 1. 启用 WebFlux

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

**注意**：与 `spring-boot-starter-web` 默认互斥（MVC），需显式选择。

---

## 2. 注解式 Controller

```java
@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderService service;

    @GetMapping("/{id}")
    public Mono<OrderDto> get(@PathVariable Long id) {
        return service.findById(id);
    }

    @GetMapping
    public Flux<OrderDto> list() {
        return service.findAll();
    }

    @PostMapping
    public Mono<OrderDto> create(@RequestBody Mono<CreateOrderRequest> req) {
        return req.flatMap(service::create);
    }
}
```

返回类型必须是 `Mono`/`Flux`（或 ResponseEntity 包装）。

---

## 3. 函数式路由

```java
@Configuration
public class RouterConfig {
    @Bean
    public RouterFunction<ServerResponse> routes(OrderHandler handler) {
        return route(GET("/orders/{id}"), handler::get)
            .andRoute(GET("/orders"), handler::list);
    }
}
```

适合 Gateway 风格、简单 API；团队更常用注解式。

---

## 4. WebClient（非阻塞 HTTP 客户端）

```java
@Bean
WebClient webClient(WebClient.Builder builder) {
    return builder.baseUrl("http://inventory-service").build();
}

public Mono<StockDto> checkStock(Long skuId) {
    return webClient.get()
        .uri("/stock/{id}", skuId)
        .retrieve()
        .onStatus(HttpStatusCode::isError, resp -> Mono.error(new RpcException()))
        .bodyToMono(StockDto.class);
}
```

**替代 RestTemplate**（阻塞，已进入维护模式）。

---

## 5. 全局异常与 Filter

```java
@Component
@Order(-2)
public class TraceIdWebFilter implements WebFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        String traceId = UUID.randomUUID().toString();
        exchange.getResponse().getHeaders().add("X-Trace-Id", traceId);
        return chain.filter(exchange);
    }
}
```

`@ControllerAdvice` 同样支持 reactive 返回 `Mono<ResponseEntity<>>`。

---

## 6. 数据访问：R2DBC

阻塞 JDBC 会卡 event loop，响应式栈用 **R2DBC**：

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
```

```java
public interface OrderRepository extends ReactiveCrudRepository<Order, Long> {
    Flux<Order> findByUserId(Long userId);
}
```

**现实**：多数企业仍 JDBC/MyBatis → 需 `subscribeOn(boundedElastic)` 包装，或混合架构。

---

## 7. Redis Reactive

```java
ReactiveStringRedisTemplate redis;

public Mono<Boolean> setKey(String k, String v) {
    return redis.opsForValue().set(k, v);
}
```

---

## 8. SSE 与 Streaming

```java
@GetMapping(value = "/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> stream() {
    return Flux.interval(Duration.ofSeconds(1))
        .map(i -> ServerSentEvent.builder("tick " + i).build());
}
```

---

## 9. 测试

```java
@WebFluxTest(OrderController.class)
class OrderControllerTest {
    @Autowired WebTestClient client;

    @Test
    void getOrder() {
        client.get().uri("/orders/1")
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.id").isEqualTo(1);
    }
}
```

---

## 10. 常见坑

- [ ] Controller 里 `.block()`
- [ ] 阻塞 JDBC 直接在 Netty 线程
- [ ] flatMap 并发过高打爆下游
- [ ] 混用 MVC 和 WebFlux 依赖冲突
- [ ] 忽略 backpressure 导致 OOM

---

## 11. 面试要点

1. WebFlux 默认用什么服务器？
2. WebClient 和 RestTemplate？
3. R2DBC 和 JDBC？
4. WebFilter 和 Servlet Filter？
5. 如何测 WebFlux？

← [01-响应式基础](./01-响应式编程基础.md) · [03-选型](./03-WebFlux与MVC选型.md)
