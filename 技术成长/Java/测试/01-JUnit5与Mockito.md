# 01 · JUnit5 与 Mockito

> **预计阅读**：90 min

---

## 1. JUnit 5 架构

```
JUnit Platform + Jupiter（API）+ Vintage（JUnit4 兼容）
```

Maven：

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
```

已含 JUnit 5、Mockito、AssertJ。

---

## 2. 基础测试

```java
@DisplayName("订单服务")
class OrderServiceTest {

    @Test
    @DisplayName("创建订单应返回 ID")
    void createOrder_shouldReturnId() {
        Order order = service.create(validRequest());
        assertThat(order.getId()).isNotNull();
    }
}
```

---

## 3. 生命周期

| 注解 | 范围 |
|------|------|
| `@BeforeAll` / `@AfterAll` | 类级，static |
| `@BeforeEach` / `@AfterEach` | 每测试方法 |

---

## 4. 断言 AssertJ（推荐）

```java
assertThat(list).hasSize(3).contains("a");
assertThatThrownBy(() -> service.invalid())
    .isInstanceOf(BusinessException.class)
    .hasMessageContaining("库存不足");
```

比 JUnit 自带 `assertEquals` 可读性更好。

---

## 5. 参数化测试

```java
@ParameterizedTest
@CsvSource({"1, true", "0, false"})
void checkStock(int qty, boolean expected) {
    assertThat(service.hasStock(qty)).isEqualTo(expected);
}

@ParameterizedTest
@MethodSource("provideOrders")
void validate(Order order) { ... }
```

---

## 6. Mockito 基础

### 6.1 创建 Mock

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock OrderRepository orderRepo;
    @Mock InventoryClient inventoryClient;
    @InjectMocks OrderService orderService;
}
```

### 6.2 Stubbing

```java
when(inventoryClient.check(100L)).thenReturn(true);
when(inventoryClient.check(999L)).thenThrow(new RpcException("timeout"));

doNothing().when(orderRepo).delete(any());
```

### 6.3 Verify

```java
verify(orderRepo, times(1)).save(argThat(o -> o.getStatus() == PAID));
verify(inventoryClient, never()).deduct(anyLong());
```

---

## 7. 高级 Mockito

| 特性 | 用途 |
|------|------|
| `@Captor` | 捕获参数断言 |
| `ArgumentMatchers` | `any()`, `eq()` |
| `Answer` | 动态返回值 |
| `spy` | 部分 mock 真实对象 |

```java
@Captor ArgumentCaptor<Order> orderCaptor;
service.pay(orderId);
verify(orderRepo).save(orderCaptor.capture());
assertThat(orderCaptor.getValue().getStatus()).isEqualTo(PAID);
```

---

## 8. 测试原则

1. **FAST**：无 DB、无网络（单元测试）
2. **独立**：测试顺序无关
3. **可重复**：不依赖环境状态
4. **测行为**不测实现细节
5. **一个测试一个断言主题**（可多个 assert）

---

## 9. 反模式

- [ ] 测试 private 方法
- [ ] Mock 过多（被测类只剩胶水）
- [ ] 测试依赖测试（共享 mutable 状态）
- [ ] `Thread.sleep` 代替 proper wait
- [ ] 只断言不抛异常，不断言返回值

---

## 10. 面试要点

1. JUnit 4 和 5 区别？
2. `@Mock` 和 `@InjectMocks`？
3. when 和 doReturn 区别？
4. verify 的作用？
5. 如何测异常？

← [00-速查](./00-速查.md) · [02-集成测试](./02-集成测试与SpringTest.md)
