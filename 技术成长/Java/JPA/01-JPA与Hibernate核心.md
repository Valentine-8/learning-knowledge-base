# 01 · JPA 与 Hibernate 核心

> **预计阅读**：90 min

---

## 1. 体系结构

```
JPA（javax/jakarta.persistence 规范）
    ↓ 实现
Hibernate ORM
    ↓ 集成
Spring Data JPA（Repository 抽象）
    ↓ 运行时
EntityManager / Session
```

---

## 2. 实体基础

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 64)
    private String orderNo;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @Version
    private Long version;  // 乐观锁

    @CreationTimestamp
    private Instant createdAt;
}
```

---

## 3. EntityManager 与持久化上下文

| 概念 | 说明 |
|------|------|
| 持久化上下文 | 一级缓存，事务级 |
| Managed | 受管状态，变更自动 flush |
| Detached | Session 外，变更不跟踪 |
| Transient | 新建未 persist |

```java
@Transactional
public void update(Long id) {
    Order order = em.find(Order.class, id);  // Managed
    order.setStatus(PAID);  // 脏检查，事务提交时 UPDATE
}
```

---

## 4. 实体状态转换

```
new → persist → Managed → flush → DB
              → detach → Detached
              → remove → Removed
```

---

## 5. Spring Data JPA Repository

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    // 派生查询
    Optional<Order> findByOrderNo(String orderNo);

    // 分页
    Page<Order> findByUserId(Long userId, Pageable pageable);

    // 修改
    @Modifying
    @Query("update Order o set o.status = :s where o.id = :id")
    int updateStatus(@Param("id") Long id, @Param("s") OrderStatus s);
}
```

`JpaRepository` 提供 CRUD + 分页 + batch。

---

## 6. 事务

```java
@Service
public class OrderService {
    @Transactional
    public Order create(CreateOrderCmd cmd) { ... }

    @Transactional(readOnly = true)
    public Order get(Long id) { ... }
}
```

- `readOnly=true`：优化 flush、连接
- 默认传播 `REQUIRED`

---

## 7. Flush 与 Clear

| 操作 | 作用 |
|------|------|
| `flush()` | 同步 SQL 到 DB，不提交事务 |
| `clear()` | 清空持久化上下文 |

批量 insert 时可分批 `flush + clear` 防内存涨。

---

## 8. Hibernate 二级缓存（了解）

```
一级：Session 级，默认开
二级：SessionFactory 级，需配 Ehcache/Redis，多实例一致性难
```

**生产常见**：关二级缓存，用 Redis 应用层缓存。

---

## 9. 配置要点

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate   # 生产不用 update/create
    show-sql: false
    properties:
      hibernate:
        format_sql: true
        jdbc.batch_size: 50
        order_inserts: true
        order_updates: true
```

---

## 10. 面试要点

1. JPA 和 Hibernate 关系？
2. 实体状态有哪些？
3. persist 和 merge 区别？
4. 一级缓存作用？
5. Spring Data JPA 原理？

← [00-速查](./00-速查.md) · [02-实体映射](./02-实体映射与关联.md)
