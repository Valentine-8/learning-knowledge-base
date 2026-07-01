# 02 · 集成测试与 Spring Test

> **预计阅读**：90 min

---

## 1. 集成测试定位

```
启动 Spring 上下文（或切片），测试多层协作
比单元测试慢，比 E2E 快
```

**适用**：Controller + Service + Repository 链路、配置绑定、Security。

---

## 2. @SpringBootTest

```java
@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerIT {

    @Autowired MockMvc mockMvc;
    @MockBean PaymentClient paymentClient;

    @Test
    void createOrder() throws Exception {
        when(paymentClient.prepay(any())).thenReturn("token");
        mockMvc.perform(post("/orders")
                .contentType(APPLICATION_JSON)
                .content(json))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists());
    }
}
```

---

## 3. 测试切片

| 注解 | 加载范围 |
|------|----------|
| `@WebMvcTest(Controller.class)` | MVC + Controller |
| `@DataJpaTest` | JPA + 内存/Testcontainers DB |
| `@JsonTest` | Jackson |
| `@RestClientTest` | RestTemplate/WebClient |

**优势**：启动快，只加载需要的 Bean。

---

## 4. @MockBean vs @Mock

| | @Mock | @MockBean |
|---|-------|-----------|
| 容器 | 无 | 替换 Spring 容器中 Bean |
| 场景 | 纯单元 | 集成测试隔离外部依赖 |

---

## 5. MockMvc

```java
mockMvc.perform(get("/orders/1")
        .header("Authorization", "Bearer " + token))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.amount").value(100));
```

配合 `@WithMockUser` 测 Security：

```java
@WithMockUser(roles = "ADMIN")
@Test void adminOnly() { ... }
```

---

## 6. @Sql 与数据准备

```java
@Test
@Sql("/testdata/orders.sql")
void listOrders() { ... }

@Transactional  // 测试后回滚
@Test
void createAndQuery() { ... }
```

**注意**：`@Transactional` 在测试里会掩盖事务传播问题，关键场景可不用。

---

## 7. TestRestTemplate / WebTestClient

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
class OrderApiIT {
    @Autowired TestRestTemplate rest;

    @Test
    void health() {
        var resp = rest.getForEntity("/actuator/health", String.class);
        assertThat(resp.getStatusCode()).isEqualTo(OK);
    }
}
```

WebFlux 用 `WebTestClient`。

---

## 8. 配置隔离

```yaml
# application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:test
  flyway:
    enabled: true
```

```java
@ActiveProfiles("test")
@SpringBootTest
class OrderIT { }
```

---

## 9. 最佳实践

- 集成测试命名 `*IT` 或放 `src/test/integration`
- Maven failsafe 插件跑集成测试（与 surefire 分离）
- 外部 RPC 一律 Mock 或 WireMock
- DB 用 H2（简单）或 Testcontainers（真实）

---

## 10. 面试要点

1. @SpringBootTest 和 @WebMvcTest 区别？
2. @MockBean 原理？
3. MockMvc 测什么？
4. 集成测试如何准备数据？
5. 如何分离单元和集成测试执行？

← [01-JUnit5](./01-JUnit5与Mockito.md) · [03-Testcontainers](./03-Testcontainers.md)
