# 03 · JPQL 与性能 N+1

> **预计阅读**：90 min

---

## 1. 查询方式

| 方式 | 说明 |
|------|------|
| 派生方法名 | `findByUserIdAndStatus` |
| `@Query` JPQL | 面向实体 |
| `@Query` native | 原生 SQL |
| Criteria API | 动态条件（类型安全） |
| Specification | Spring Data 封装 Criteria |

---

## 2. JPQL 基础

```java
@Query("select o from Order o where o.userId = :uid and o.status = :st")
List<Order> findUserOrders(@Param("uid") Long uid, @Param("st") OrderStatus st);

@Query("select new com.example.OrderDto(o.id, o.orderNo) from Order o where o.userId = :uid")
List<OrderDto> findDtos(@Param("uid") Long uid);
```

**注意**：JPQL 操作实体名和属性名，不是表名列名。

---

## 3. N+1 问题

```java
List<Order> orders = orderRepo.findByUserId(1L);  // 1 条 SQL
orders.forEach(o -> o.getItems().size());         // N 条 SQL
```

### 解决方案

**① fetch join**

```java
@Query("select distinct o from Order o join fetch o.items where o.userId = :uid")
List<Order> findWithItems(@Param("uid") Long uid);
```

**② @EntityGraph**

```java
@EntityGraph(attributePaths = {"items"})
List<Order> findByUserId(Long userId);
```

**③ @BatchSize**

```java
@OneToMany
@BatchSize(size = 20)
private List<OrderItem> items;
```

**④ DTO 投影**（只查需要的列）

```java
@Query("select o.id as id, o.orderNo as orderNo from Order o")
List<OrderSummary> findSummaries();
```

---

## 4. 分页

```java
Page<Order> page = orderRepo.findByUserId(userId, PageRequest.of(0, 20, Sort.by("createdAt").descending()));
```

**fetch join + 分页陷阱**：内存分页，数据量大用子查询或单独查 items。

---

## 5. 动态查询 Specification

```java
public static Specification<Order> hasUser(Long uid) {
    return (root, q, cb) -> cb.equal(root.get("userId"), uid);
}

orderRepo.findAll(Specification.where(hasUser(1L)).and(hasStatus(PAID)));
```

---

## 6. 批量操作

```java
@Modifying(clearAutomatically = true)
@Query("update Order o set o.status = PAID where o.id in :ids")
int batchUpdate(@Param("ids") List<Long> ids);
```

需 `@Transactional`；大批量分批执行。

---

## 7. 性能 checklist

- [ ] 生产关闭 `show-sql`
- [ ] 开启 `jdbc.batch_size`
- [ ] 索引覆盖查询条件
- [ ] 避免 SELECT 全实体再转 DTO
- [ ] 慢查询日志 + p6spy（开发）
- [ ] 统计查询考虑原生 SQL 或只读副本

---

## 8. Hibernate 统计

```yaml
spring.jpa.properties.hibernate.generate_statistics: true
```

开发环境看 Session Metrics；生产用 APM。

---

## 9. 与 MySQL 索引配合

- `where user_id = ? order by created_at desc` → 复合索引 `(user_id, created_at)`
- `like '%abc'` 无法走索引
- 乐观锁 version 列自动参与 WHERE

---

## 10. 面试要点

1. N+1 是什么？怎么解？
2. fetch join 和 EntityGraph？
3. JPQL 和 SQL 区别？
4. 分页 + fetch join 问题？
5. @Modifying 注意什么？

← [02-实体映射](./02-实体映射与关联.md) · [04-选型](./04-JPA与MyBatis选型.md)
