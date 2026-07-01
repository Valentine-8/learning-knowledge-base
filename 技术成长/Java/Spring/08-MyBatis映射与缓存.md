# 08 · MyBatis 映射与缓存

> **目标读者**：掌握 Mapper 映射、动态 SQL、#{} 防注入、一二级缓存、N+1 与 PageHelper。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. MyBatis 在 Spring 中的位置

```
Controller → Service(@Transactional) → Mapper 接口 → MyBatis SqlSession → JDBC
```

**Mapper 是接口**，实现由 MyBatis 动态代理生成。

```java
@Mapper
public interface OrderMapper {
    Order selectById(@Param("id") Long id);
    int insert(Order order);
}
```

```xml
<!-- OrderMapper.xml -->
<mapper namespace="com.example.mapper.OrderMapper">
  <select id="selectById" resultType="com.example.domain.Order">
    SELECT * FROM orders WHERE id = #{id}
  </select>
</mapper>
```

---

## 2. #{} 与 ${}

| | #{} | ${} |
|---|-----|-----|
| 方式 | **预编译** PreparedStatement | 字符串拼接 |
| 安全 | 防 SQL 注入 | **有注入风险** |
| 场景 | 值 | 动态表名、ORDER BY 列名（白名单） |

```xml
<!-- 安全 -->
WHERE name = #{name}

<!-- 危险：用户输入直接拼 -->
ORDER BY ${column}   <!-- 必须白名单校验 column -->

<!-- 正确动态排序 -->
ORDER BY
<choose>
  <when test="sort == 'created_at'">created_at</when>
  <otherwise>id</otherwise>
</choose>
```

---

## 3. 结果映射

```xml
<resultMap id="OrderMap" type="com.example.domain.Order">
  <id property="id" column="id"/>
  <result property="userId" column="user_id"/>
  <result property="createdAt" column="created_at"/>
  <association property="user" javaType="User">
    <id property="id" column="user_id"/>
    <result property="name" column="user_name"/>
  </association>
  <collection property="items" ofType="OrderItem">
    <id property="id" column="item_id"/>
  </collection>
</resultMap>
```

**驼峰**：`mapUnderscoreToCamelCase=true`。

---

## 4. 动态 SQL

```xml
<select id="search" resultType="Order">
  SELECT * FROM orders
  <where>
    <if test="userId != null">AND user_id = #{userId}</if>
    <if test="status != null">AND status = #{status}</if>
    <if test="ids != null and ids.size() > 0">
      AND id IN
      <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
      </foreach>
    </if>
  </where>
</select>
```

| 标签 | 作用 |
|------|------|
| if / choose | 条件 |
| where / set | 智能 AND/逗号 |
| foreach | IN 循环 |
| trim | 自定义前缀后缀 |

---

## 5. 一级缓存

**范围**：同一 **SqlSession**。

```
第一次 selectById(1) → 查 DB → 放入 LocalCache
同 Session 第二次 selectById(1) → 命中缓存
```

| 清空时机 | |
|----------|---|
| update/insert/delete | 该 namespace 相关 |
| `sqlSession.clearCache()` | 手动 |
| 不同 SqlSession | 不共享 |

**Spring 整合**：每个 `@Transactional` 方法通常同一 SqlSession → 事务内重复查询可能命中一级缓存。

**关闭**：`localCacheScope=STATEMENT`（每次语句后清）。

---

## 6. 二级缓存

**范围**：同一 **Mapper namespace**，跨 SqlSession。

```xml
<cache eviction="LRU" flushInterval="60000" size="512" readOnly="true"/>
```

| 注意 | |
|------|---|
| 实体需 Serializable | 序列化存缓存 |
| 多表关联 | 脏读风险，生产 **慎用** |
| 分布式 | 需 Redis 等集中缓存，非默认二级缓存 |

**生产建议**：查询缓存用 **Redis**；MyBatis 二级缓存多 **关闭**。

---

## 7. N+1 问题

```java
List<Order> orders = orderMapper.selectAll();  // 1 次
for (Order o : orders) {
    o.setItems(itemMapper.selectByOrderId(o.getId()));  // N 次
}
```

**解决**：

```xml
<!-- 1. JOIN 一次查出 -->
<select id="selectWithItems" resultMap="OrderWithItemsMap">
  SELECT o.*, i.id item_id, i.product_name
  FROM orders o LEFT JOIN order_items i ON o.id = i.order_id
</select>

<!-- 2. 批量 IN -->
select * from order_items where order_id in (...)
```

MyBatis **lazy loading**（association fetchType=lazy）不当使用也会 N+1。

---

## 8. 分页

**PageHelper**：

```java
PageHelper.startPage(pageNum, pageSize);
List<Order> list = orderMapper.selectByCondition(query);
PageInfo<Order> page = new PageInfo<>(list);
```

原理：ThreadLocal + 拦截 SQL 加 `LIMIT`。

**MyBatis-Plus**：`IPage` 内置。

---

## 9. 与 JPA 选型

| | MyBatis | JPA/Hibernate |
|---|---------|---------------|
| SQL 控制 | **完全** | 自动生成，复杂 SQL 弱 |
| 学习曲线 | SQL 熟悉即可 | 对象关系、懒加载 |
| 批量/报表 | 强 | 一般 |
| 国内 | 互联网常用 | 企业、CRUD 快 |

7 年：**两者都要会**；复杂 SQL、性能调优 MyBatis 更多。

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| #{} 和 ${}？ | 预编译 vs 拼接 |
| 一级二级缓存？ | Session vs Mapper namespace |
| 何时清一级缓存？ | 写操作、clearCache |
| N+1 怎么解决？ | JOIN、批量 IN、避免循环查 |
| Mapper 接口如何工作？ | JDK 动态代理 + SqlSession |

---

→ [09-生产案例与面试题库](./09-生产案例与面试题库.md)

← [07-Spring Security 与 JWT](./07-SpringSecurity与JWT.md)
