# 04 · 与 Java 集成

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 依赖与配置

### Spring Boot 3.x

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>
```

```yaml
spring:
  data:
    mongodb:
      uri: mongodb://app:secret@mongo1:27017,mongo2:27017/shop?replicaSet=rs0&authSource=admin
      # 或分开配置
      # host: localhost
      # port: 27017
      # database: shop
      # username: app
      # password: secret
```

| 配置项 | 说明 |
|--------|------|
| `uri` | 推荐，支持副本集参数 |
| `auto-index-creation` | 开发 true，生产 false（手动建索引） |
| 连接池 | 默认内置，可配 `maxPoolSize` |

---

## 2. 实体映射

```java
@Document(collection = "orders")
public class Order {
    @Id
    private String id;                    // 或 ObjectId

    @Indexed
    private Long userId;

    private List<OrderItem> items;        // 嵌套文档

    @Field("total_amount")               // 字段名映射
    private BigDecimal totalAmount;

    @CreatedDate
    private Instant createdAt;

    @Version
    private Long version;                 // 乐观锁
}
```

| 注解 | 作用 |
|------|------|
| `@Document` | 指定集合名 |
| `@Id` | 主键 |
| `@Field` | BSON 字段名 |
| `@Indexed` | 声明索引（auto-index 开启时生效） |
| `@DBRef` | 引用其他文档（慎用，性能差） |
| `@Version` | 乐观锁 |
| `@CreatedDate` / `@LastModifiedDate` | 审计字段，需 `@EnableMongoAuditing` |

---

## 3. Repository 模式

```java
public interface OrderRepository extends MongoRepository<Order, String> {

    List<Order> findByUserIdAndStatus(Long userId, String status);

    @Query("{ 'userId': ?0, 'totalAmount': { $gte: ?1 } }")
    List<Order> findLargeOrders(Long userId, BigDecimal minAmount);

    @Aggregation(pipeline = {
        "{ $match: { status: 'paid' } }",
        "{ $group: { _id: '$userId', total: { $sum: '$totalAmount' } } }"
    })
    List<UserTotal> sumByUser();
}
```

| 能力 | 说明 |
|------|------|
| 方法名推导 | `findByXxxAndYyy` |
| `@Query` | 原生 JSON 查询 |
| `@Aggregation` | 聚合管道 |
| `Pageable` | 分页 `findByStatus(String status, Pageable page)` |

---

## 4. MongoTemplate 灵活操作

Repository 不够用时，注入 `MongoTemplate`：

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final MongoTemplate mongoTemplate;

    public void batchUpdateStatus(List<String> ids, String status) {
        Query query = Query.query(Criteria.where("_id").in(ids));
        Update update = new Update().set("status", status).currentDate("updatedAt");
        mongoTemplate.updateMulti(query, update, Order.class);
    }

    public List<Order> cursorPage(Long userId, String lastId, int size) {
        Criteria criteria = Criteria.where("userId").is(userId);
        if (lastId != null) {
            criteria.and("_id").gt(new ObjectId(lastId));
        }
        return mongoTemplate.find(
            Query.query(criteria).with(Sort.by("_id")).limit(size),
            Order.class
        );
    }
}
```

---

## 5. 事务支持

```java
@Configuration
@EnableMongoRepositories
@EnableTransactionManagement
public class MongoConfig {

    @Bean
    MongoTransactionManager transactionManager(MongoDatabaseFactory factory) {
        return new MongoTransactionManager(factory);
    }
}

@Service
public class OrderWriteService {
    @Transactional
    public void createOrder(Order order) {
        orderRepository.save(order);
        inventoryRepository.decrementStock(order.getItems());
    }
}
```

| 前提 | 说明 |
|------|------|
| 副本集 | 单节点不支持事务 |
| 性能 | 短事务，避免跨多集合长操作 |

---

## 6. 读写分离

```java
@Configuration
public class MongoReadConfig {

    @Bean
    MongoClientSettingsBuilderCustomizer readPrefCustomizer() {
        return builder -> builder.readPreference(ReadPreference.secondaryPreferred());
    }
}
```

或在 `@Transactional(readOnly = true)` 方法上使用只读偏好（需自定义 `AbstractMongoClientConfiguration`）。

---

## 7. 与 MySQL 混用场景

| 模式 | 说明 |
|------|------|
| 双写 | 订单核心 MySQL，日志/行为 MongoDB |
| CQRS | 写 MySQL，异步同步到 Mongo 读模型 |
| 选型分离 | 强一致业务 MySQL，灵活文档 MongoDB |

```java
// 同一 Spring Boot 项目
@Transactional("mysqlTransactionManager")   // MySQL
public void createOrderInMysql(...) { }

@Transactional("mongoTransactionManager") // MongoDB
public void writeAuditLog(...) { }
```

---

## 8. 常见问题

| 问题 | 原因与解决 |
|------|-----------|
| `_id` 类型不匹配 | String vs ObjectId，统一一种 |
| 时区偏移 | 存 UTC Instant，展示层转换 |
| 索引未生效 | 生产关闭 auto-index，CI 建索引 |
| 连接超时 | 检查 replicaSet 名称、防火墙 |
| BigDecimal | 用 `@Field(targetType = DECIMAL128)` |

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| Spring Data | Repository + MongoTemplate 组合 |
| 映射 | 嵌套 POJO 代替 @DBRef |
| 事务 | 副本集 + 短事务 |
| 分页 | _id 游标优于 skip |

---

← [03 副本集与分片](./03-副本集与分片.md) · [05 生产案例 →](./05-生产案例与面试题库.md)
