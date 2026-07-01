# 05 · Spring MVC 与 Web 层

> **目标读者**：掌握 DispatcherServlet 全流程、Filter/Interceptor 区别、参数校验、全局异常与 REST 最佳实践。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 请求全链路

```
HTTP Request
  → Servlet Filter 链（Spring Security Filter 也在此）
  → DispatcherServlet
       → HandlerMapping 找 Handler（Controller 方法）
       → HandlerAdapter 执行（RequestMappingHandlerAdapter）
       → 参数解析（ArgumentResolver）
       → Controller 方法
       → 返回值处理（HandlerMethodReturnValueHandler）
       → HttpMessageConverter 写 JSON（MappingJackson2HttpMessageConverter）
  → HTTP Response
```

```
┌──────────┐   ┌───────────────────┐   ┌─────────────┐   ┌──────┐
│  Filter  │ → │ DispatcherServlet │ → │ Interceptor │ → │ Ctrl │
└──────────┘   └───────────────────┘   └─────────────┘   └──────┘
```

---

## 2. DispatcherServlet 核心组件

| 组件 | 作用 |
|------|------|
| HandlerMapping | URL → HandlerExecutionChain（Handler + Interceptors） |
| HandlerAdapter | 适配不同 Handler 类型执行 |
| HandlerExceptionResolver | 异常 → ModelAndView / ResponseEntity |
| ViewResolver | 视图名 → View（REST 少用） |
| HttpMessageConverter | 读写 Request/Response Body |

**Boot 默认**：`RequestMappingHandlerMapping` + `RequestMappingHandlerAdapter`。

---

## 3. Controller 与 REST

```java
@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @GetMapping("/{id}")
    public OrderDto get(@PathVariable Long id) {
        return orderService.getById(id);
    }

    @PostMapping
    public ResponseEntity<OrderDto> create(@Valid @RequestBody CreateOrderRequest req) {
        OrderDto dto = orderService.create(req);
        return ResponseEntity.status(HttpStatus.CREATED).body(dto);
    }

    @GetMapping
    public Page<OrderDto> list(@ParameterObject OrderQuery query, Pageable pageable) {
        return orderService.list(query, pageable);
    }
}
```

---

## 4. 参数绑定

| 注解 | 来源 |
|------|------|
| `@RequestParam` | Query / form |
| `@PathVariable` | URI 模板 |
| `@RequestBody` | JSON Body |
| `@RequestHeader` | Header |
| `@CookieValue` | Cookie |
| `@ModelAttribute` | form 绑定对象 |

**校验**：

```java
public record CreateOrderRequest(
    @NotNull Long userId,
    @Size(min = 1, max = 50) List<@Valid LineItem> items
) { }
```

```java
@PostMapping
public void create(@Valid @RequestBody CreateOrderRequest req) { }
```

失败 → `MethodArgumentNotValidException` → 全局处理返回 400。

---

## 5. Filter vs HandlerInterceptor

| | Filter | HandlerInterceptor |
|---|--------|-------------------|
| 规范 | Servlet | Spring MVC |
| 范围 | 所有 Servlet | DispatcherServlet 管理的 Handler |
| 方法 | doFilter | preHandle / postHandle / afterCompletion |
| 能否拿 Handler | 否 | 是 |
| 典型 | 编码、CORS、Security | 登录态、日志、权限注解 |

```java
@Component
public class TraceInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
        MDC.put("traceId", req.getHeader("X-Trace-Id"));
        return true;
    }
    @Override
    public void afterCompletion(..., Exception ex) {
        MDC.clear();
    }
}
```

**注册**：

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(traceInterceptor).addPathPatterns("/api/**");
    }
}
```

**顺序**：Filter（Security 在内）→ Interceptor pre → Controller → Interceptor post → Filter 返回。

---

## 6. 全局异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiError> handleBiz(BusinessException ex) {
        return ResponseEntity.status(ex.getCode()).body(ApiError.of(ex));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiError> handleValid(MethodArgumentNotValidException ex) {
        String msg = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining("; "));
        return ResponseEntity.badRequest().body(ApiError.badRequest(msg));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiError> handleOther(Exception ex) {
        log.error("unexpected", ex);
        return ResponseEntity.internalServerError().body(ApiError.internal());
    }
}
```

**统一响应体**：

```java
public record ApiResponse<T>(int code, String message, T data) {
    public static <T> ApiResponse<T> ok(T data) { return new ApiResponse<>(0, "ok", data); }
}
```

---

## 7. CORS

```java
@Bean
public WebMvcConfigurer corsConfigurer() {
    return new WebMvcConfigurer() {
        @Override
        public void addCorsMappings(CorsRegistry registry) {
            registry.addMapping("/api/**")
                .allowedOrigins("https://www.example.com")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowCredentials(true);
        }
    };
}
```

网关层（Gateway/Nginx）也可统一 CORS，避免重复。

---

## 8. 内容协商与 Jackson

```yaml
spring:
  jackson:
    default-property-inclusion: non_null
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: Asia/Shanghai
    serialization:
      write-dates-as-timestamps: false
```

**LocalDateTime**：注册 `JavaTimeModule`（Boot 自动）。

---

## 9. 异步与 SSE

```java
@GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> stream() {
    return Flux.interval(Duration.ofSeconds(1))
        .map(i -> ServerSentEvent.builder("tick " + i).build());
}
```

需 **WebFlux** 或 MVC 6.1+ 异步支持；传统 MVC 可用 `SseEmitter`。

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| Spring MVC 流程？ | DispatcherServlet → Mapping → Adapter → 参数 → 返回 → Converter |
| Filter 和 Interceptor？ | Servlet 层 vs MVC 层；范围与能力不同 |
| @Controller 和 @RestController？ | 后者 = @Controller + @ResponseBody |
| 如何统一异常？ | @ControllerAdvice + @ExceptionHandler |
| PUT 和 PATCH？ | PUT 全量替换；PATCH 部分更新（需约定） |

---

→ [06-事务传播与失效](./06-事务传播与失效.md)

← [04-Spring Boot 自动配置](./04-SpringBoot自动配置.md)
