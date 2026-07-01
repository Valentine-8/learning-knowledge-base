# 03 · Testcontainers

> **预计阅读**：80 min

---

## 1. 为什么 Testcontainers

| 方案 | 问题 |
|------|------|
| H2 内存库 | 与 MySQL 语法/行为差异 |
| 共享测试 DB |  flaky、污染 |
| Mock Repository | 测不到 SQL 问题 |
| **Testcontainers** | 真实 Docker 镜像，CI 可重复 |

---

## 2. 依赖

```xml
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>mysql</artifactId>
  <scope>test</scope>
</dependency>
```

**要求**：本地/CI 有 Docker。

---

## 3. 基础用法

```java
@Testcontainers
class OrderRepositoryIT {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
        .withDatabaseName("test")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
    }

    @Autowired OrderRepository repo;

    @Test
    void saveAndFind() {
        repo.save(order);
        assertThat(repo.findById(order.getId())).isPresent();
    }
}
```

---

## 4. 与 @DataJpaTest 结合

```java
@DataJpaTest
@Testcontainers
@AutoConfigureTestDatabase(replace = NONE)
class OrderJpaIT { ... }
```

---

## 5. 常用模块

| 模块 | 用途 |
|------|------|
| mysql / postgresql | 关系库 |
| redis | 缓存 |
| kafka | 消息 |
| localstack | AWS 模拟 |
| generic | 任意镜像 |

```java
@Container
static GenericContainer<?> redis = new GenericContainer<>("redis:7")
    .withExposedPorts(6379);
```

---

## 6. 性能优化

| 手段 | 说明 |
|------|------|
| static @Container | 同类测试共享一个容器 |
| Ryuk | 自动清理，勿关除非知后果 |
| 镜像 pin 版本 | 避免 pull 最新 |
| CI 缓存 Docker layer | GitHub Actions cache |
| testcontainers.reuse.enable | 本地复用（开发用） |

---

## 7. Spring Boot 3.1+ 原生支持

```yaml
# application-test.yml
spring:
  testcontainers:
    enabled: true
```

或使用 `@ServiceConnection`：

```java
@Container
@ServiceConnection
static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0");
```

自动配置 DataSource，无需 DynamicPropertySource。

---

## 8. 与 Flyway/Liquibase

```java
@Container
static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0");

// Spring Boot 启动时 Flyway 自动 migrate
@SpringBootTest
@ActiveProfiles("test")
```

保证 schema 与生产一致。

---

## 9. 注意事项

- CI 需 Docker-in-Docker 或 socket mount
- 并行测试时端口冲突 → 每容器随机端口
- 容器启动慢 → 控制集成测试数量
- 不适合纯单元测试

---

## 10. 面试要点

1. Testcontainers 解决什么问题？
2. 和 H2 对比？
3. @DynamicPropertySource 作用？
4. 如何加速 Testcontainers？
5. CI 如何配置 Docker？

← [02-集成测试](./02-集成测试与SpringTest.md) · [04-测试策略](./04-测试策略与覆盖率.md)
